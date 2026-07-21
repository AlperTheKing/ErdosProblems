#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace fs = std::filesystem;

static std::string env(const char* name, const char* fallback = "") {
  const char* value = std::getenv(name);
  return value ? value : fallback;
}

static void atomic_write(const fs::path& path, const std::string& text) {
  const fs::path tmp = path.string() + ".tmp";
  { std::ofstream out(tmp, std::ios::binary); out << text; }
  std::error_code ec;
  fs::rename(tmp, path, ec);
  if (ec) throw std::runtime_error("rename failed");
}

static std::string candidate() {
  std::string result = "{\"n\":19,\"out_neighbors\":[";
  for (int i = 0; i < 19; ++i) {
    if (i) result += ',';
    result += "[]";
  }
  return result + "]}\n";
}

int main(int argc, char** argv) {
  const std::string mode = env("SSNC_FAKE_MODE", "normal");
  if (argc == 2 && std::string(argv[1]).rfind("--", 0) != 0) {
    const int code = std::stoi(env("SSNC_FAKE_VERIFIER_EXIT", "0"));
    std::cout << "{\"status\":\"" << (code == 0 ? "VERIFIED_COUNTEREXAMPLE" : "VALID_GRAPH_NOT_COUNTEREXAMPLE") << "\"}\n";
    return code;
  }
  std::vector<std::string> args(argv + 1, argv + argc);
  if (!args.empty() && args[0] == "--self-test") {
    if (mode == "selftest_fail") {
      std::cout << "{\"status\":\"SELF_TEST_FAIL\",\"production_run\":false,\"failures\":1}\n";
      return 9;
    }
    std::cout << "{\"status\":\"SELF_TEST_PASS\",\"production_run\":false,\"failures\":0}\n";
    return 0;
  }
  int threads = 0;
  int seconds = 0;
  fs::path output;
  for (std::size_t i = 0; i + 1 < args.size(); i += 2) {
    if (args[i] == "--threads") threads = std::stoi(args[i + 1]);
    else if (args[i] == "--seconds") seconds = std::stoi(args[i + 1]);
    else if (args[i] == "--output-dir") output = args[i + 1];
  }
  if (threads <= 0 || seconds <= 0 || output.empty()) return 8;
  fs::create_directories(output);
  const bool production = threads > 1;
  if ((mode == "canary_timeout" && !production) ||
      (mode == "production_timeout" && production)) {
    std::this_thread::sleep_for(std::chrono::seconds(seconds + (production ? 4 : 75)));
    return 0;
  }
  if (production && mode == "partial_candidate") {
    { std::ofstream out(output / "hit_candidate.json", std::ios::binary); out << '{'; }
    std::this_thread::sleep_for(std::chrono::seconds(4));
    return 0;
  }
  if (production && mode == "candidate") {
    atomic_write(output / "hit_candidate.json", candidate());
    std::this_thread::sleep_for(std::chrono::seconds(4));
    return 0;
  }
  std::this_thread::sleep_for(std::chrono::seconds(seconds));
  atomic_write(output / "summary.json",
               "{\"status\":\"NO_HIT\",\"threads\":" + std::to_string(threads) +
               ",\"seconds\":" + std::to_string(seconds) + "}\n");
  std::cout << "{\"status\":\"NO_HIT\"}\n";
  return 0;
}
