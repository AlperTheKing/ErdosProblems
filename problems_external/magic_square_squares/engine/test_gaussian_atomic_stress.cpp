#define main gaussian_center_embedded_main
#include "gaussian_center.cpp"
#undef main

#include <atomic>
#include <chrono>
#include <filesystem>
#include <iostream>
#include <regex>
#include <stdexcept>
#include <string>
#include <thread>

namespace fs = std::filesystem;

namespace {

std::string payload(unsigned sequence) {
    return "{\"sequence\":" + std::to_string(sequence) +
           ",\"padding\":\"" + std::string(128, 'A') + "\"}\n";
}

void require_complete_payload(const std::string& contents) {
    static const std::regex pattern(
        "^\\{\\\"sequence\\\":[0-9]+,\\\"padding\\\":\\\"A{128}\\\"\\}\\n$");
    if (!std::regex_match(contents, pattern)) {
        throw std::runtime_error(
            "reader observed a partial or malformed payload");
    }
}

}  // namespace

int main() {
#ifndef _WIN32
    std::cout
        << "{\"ok\":true,\"skipped\":\"Windows-only locking stress\"}\n";
    return 0;
#else
    const auto tick =
        std::chrono::steady_clock::now().time_since_epoch().count();
    const fs::path calibration_root =
        fs::absolute(fs::path(__FILE__)).parent_path() / "calibration";
    const fs::path directory = calibration_root /
        ("gaussian-atomic-stress-" + std::to_string(GetCurrentProcessId()) +
         "-" + std::to_string(tick));
    const fs::path target = directory / "summary.json";
    fs::create_directories(directory);
    atomic_write(target, payload(0));

    std::atomic<bool> stop{false};
    std::atomic<bool> first_lock{false};
    std::atomic<unsigned> valid_reads{0};
    std::atomic<unsigned> open_retries{0};
    std::exception_ptr reader_error;

    std::thread reader([&]() {
        try {
            while (!stop.load(std::memory_order_acquire)) {
                HANDLE handle = CreateFileW(
                    target.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr,
                    OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
                if (handle == INVALID_HANDLE_VALUE) {
                    const DWORD error = GetLastError();
                    if (error == ERROR_SHARING_VIOLATION ||
                        error == ERROR_LOCK_VIOLATION ||
                        error == ERROR_FILE_NOT_FOUND) {
                        open_retries.fetch_add(1, std::memory_order_relaxed);
                        std::this_thread::yield();
                        continue;
                    }
                    throw std::runtime_error(
                        "reader CreateFileW failed with Windows error " +
                        std::to_string(error));
                }

                first_lock.store(true, std::memory_order_release);
                LARGE_INTEGER size{};
                if (!GetFileSizeEx(handle, &size) || size.QuadPart < 0 ||
                    size.QuadPart > 4096) {
                    CloseHandle(handle);
                    throw std::runtime_error("reader GetFileSizeEx failed");
                }
                std::string contents(
                    static_cast<std::size_t>(size.QuadPart), '\0');
                DWORD bytes_read = 0;
                if (!ReadFile(handle, contents.data(),
                              static_cast<DWORD>(contents.size()), &bytes_read,
                              nullptr) ||
                    bytes_read != contents.size()) {
                    CloseHandle(handle);
                    throw std::runtime_error("reader ReadFile failed");
                }
                require_complete_payload(contents);
                valid_reads.fetch_add(1, std::memory_order_relaxed);

                // No FILE_SHARE_DELETE: this deterministically exercises the
                // writer's sharing-violation retry path.
                Sleep(valid_reads.load(std::memory_order_relaxed) == 1 ? 12
                                                                       : 1);
                CloseHandle(handle);
                Sleep(1);
            }
        } catch (...) {
            reader_error = std::current_exception();
            stop.store(true, std::memory_order_release);
        }
    });

    while (!first_lock.load(std::memory_order_acquire)) {
        if (stop.load(std::memory_order_acquire)) {
            reader.join();
            if (reader_error) {
                std::rethrow_exception(reader_error);
            }
            throw std::runtime_error(
                "reader stopped before acquiring its first lock");
        }
        std::this_thread::yield();
    }

    const u64 retries_before =
        g_atomic_replace_transient_retries.load(std::memory_order_relaxed);
    constexpr unsigned kWrites = 2000;
    try {
        for (unsigned sequence = 1; sequence <= kWrites; ++sequence) {
            atomic_write(target, payload(sequence));
        }
    } catch (...) {
        stop.store(true, std::memory_order_release);
        reader.join();
        throw;
    }
    stop.store(true, std::memory_order_release);
    reader.join();
    if (reader_error) {
        std::rethrow_exception(reader_error);
    }

    const u64 retries_after =
        g_atomic_replace_transient_retries.load(std::memory_order_relaxed);
    const u64 transient_retries = retries_after - retries_before;
    if (transient_retries == 0) {
        throw std::runtime_error(
            "stress did not exercise the transient retry path");
    }
    if (valid_reads.load(std::memory_order_relaxed) < 2) {
        throw std::runtime_error(
            "reader completed too few successful opens");
    }
    if (read_file(target) != payload(kWrites)) {
        throw std::runtime_error("final atomic payload mismatch");
    }

    const fs::path directory_target = directory / "directory-target";
    fs::create_directory(directory_target);
    bool nontransient_rejected_once = false;
    try {
        atomic_write(directory_target, payload(kWrites + 1));
    } catch (const std::runtime_error& error) {
        nontransient_rejected_once =
            std::string(error.what()).find("attempts 1)") !=
            std::string::npos;
    }
    if (!nontransient_rejected_once) {
        throw std::runtime_error(
            "nontransient replacement was not rejected on first attempt");
    }

    std::error_code ignored;
    fs::remove_all(directory, ignored);
    std::cout << "{\"ok\":true,\"writes\":" << kWrites
              << ",\"valid_reads\":"
              << valid_reads.load(std::memory_order_relaxed)
              << ",\"writer_transient_retries\":" << transient_retries
              << ",\"reader_open_retries\":"
              << open_retries.load(std::memory_order_relaxed)
              << ",\"nontransient_attempts\":1}\n";
    return 0;
#endif
}
