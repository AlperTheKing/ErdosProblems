#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

using u64 = std::uint64_t;
using u128 = unsigned __int128;
using Poly64 = std::vector<u64>;

struct BranchType {
    bool starred;
    int children;
    int pendant;
};

struct Entry {
    std::string label;
    int order;
    Poly64 poly;
};

static std::string dec(u128 x) {
    if (x == 0) return "0";
    std::string s;
    while (x) {
        s.push_back(char('0' + x % 10));
        x /= 10;
    }
    std::reverse(s.begin(), s.end());
    return s;
}

static Poly64 add(const Poly64& a, const Poly64& b) {
    Poly64 r(std::max(a.size(), b.size()));
    for (std::size_t i = 0; i < r.size(); ++i) {
        u128 z = (i < a.size() ? a[i] : 0) + (u128)(i < b.size() ? b[i] : 0);
        if (z > UINT64_MAX) throw std::overflow_error("tree coefficient overflow in add");
        r[i] = (u64)z;
    }
    return r;
}

static Poly64 mul(const Poly64& a, const Poly64& b) {
    Poly64 r(a.size() + b.size() - 1);
    for (std::size_t i = 0; i < a.size(); ++i) {
        for (std::size_t j = 0; j < b.size(); ++j) {
            u128 z = (u128)r[i + j] + (u128)a[i] * b[j];
            if (z > UINT64_MAX) throw std::overflow_error("tree coefficient overflow in mul");
            r[i + j] = (u64)z;
        }
    }
    return r;
}

static std::pair<std::vector<std::vector<int>>, std::string>
build_bush(const std::vector<int>& combo, const std::vector<BranchType>& types) {
    std::vector<std::vector<int>> adj(1);
    auto make_vertex = [&]() {
        adj.emplace_back();
        return (int)adj.size() - 1;
    };
    auto edge = [&](int u, int v) {
        adj[u].push_back(v);
        adj[v].push_back(u);
    };
    std::ostringstream label;
    label << "bush(";
    bool first_type = true;
    for (int idx : combo) {
        const auto& t = types[idx];
        if (!first_type) label << ",";
        first_type = false;
        label << (t.starred ? "s" : "u") << t.children << "p" << t.pendant;
        int b = make_vertex();
        edge(0, b);
        for (int j = 0; j < t.children; ++j) {
            int child = make_vertex();
            edge(b, child);
            int prev = child;
            int depth = t.pendant + (t.starred && j == 0 ? 1 : 0);
            for (int q = 0; q < depth; ++q) {
                int next = make_vertex();
                edge(prev, next);
                prev = next;
            }
        }
    }
    label << ")|n=" << adj.size();
    return {std::move(adj), label.str()};
}
namespace {
static std::pair<std::vector<std::vector<int>>, std::string>
build_literature_tree(int m, int n, bool starred) {
    std::vector<std::vector<int>> adj(1);
    auto make_vertex = [&]() {
        adj.emplace_back();
        return (int)adj.size() - 1;
    };
    auto edge = [&](int u, int v) {
        adj[u].push_back(v);
        adj[v].push_back(u);
    };
    const int degrees[3] = {3, m, n};
    for (int bi = 0; bi < 3; ++bi) {
        int branch = make_vertex();
        edge(0, branch);
        for (int j = 0; j < degrees[bi]; ++j) {
            int child = make_vertex();
            int grandchild = make_vertex();
            edge(branch, child);
            edge(child, grandchild);
            if (starred && bi == 0 && j == 0) {
                int x = make_vertex();
                int y = make_vertex();
                edge(grandchild, x);
                edge(x, y);
            }
        }
    }
    std::ostringstream label;
    label << (starred ? "Tstar_3_" : "T_3_") << m << "_" << n
          << "|n=" << adj.size();
    return {std::move(adj), label.str()};
}

}

static Poly64 indpoly_tree(const std::vector<std::vector<int>>& adj) {
    const int n = (int)adj.size();
    std::vector<int> parent(n, -2), order;
    order.reserve(n);
    parent[0] = -1;
    order.push_back(0);
    for (std::size_t q = 0; q < order.size(); ++q) {
        int v = order[q];
        for (int w : adj[v]) {
            if (parent[w] == -2) {
                parent[w] = v;
                order.push_back(w);
            }
        }
    }
    if ((int)order.size() != n) throw std::runtime_error("disconnected bush");
    std::vector<Poly64> A(n), B(n);
    for (auto it = order.rbegin(); it != order.rend(); ++it) {
        int v = *it;
        Poly64 pa{1}, pb{1};
        bool leaf = true;
        for (int w : adj[v]) {
            if (parent[w] == v) {
                leaf = false;
                pa = mul(pa, add(A[w], B[w]));
                pb = mul(pb, A[w]);
            }
        }
        if (leaf) {
            A[v] = {1};
            B[v] = {0, 1};
        } else {
            A[v] = std::move(pa);
            B[v].assign(pb.size() + 1, 0);
            std::copy(pb.begin(), pb.end(), B[v].begin() + 1);
        }
    }
    return add(A[0], B[0]);
}

static bool unimodal64(const Poly64& p) {
    bool falling = false;
    for (std::size_t k = 0; k + 1 < p.size(); ++k) {
        if (p[k] > p[k + 1]) falling = true;
        else if (falling && p[k] < p[k + 1]) return false;
    }
    return true;
}

static bool logconcave(const Poly64& p) {
    for (std::size_t k = 1; k + 1 < p.size(); ++k) {
        if ((u128)p[k] * p[k] < (u128)p[k - 1] * p[k + 1]) return false;
    }
    return true;
}

struct Catalog {
    std::vector<Entry> entries;
    std::uint64_t scanned = 0;
    std::uint64_t single_hits = 0;
};

static Catalog generate_catalog() {
    std::vector<BranchType> types;
    for (int c = 2; c <= 6; ++c) {
        for (int L = 1; L <= 3; ++L) {
            types.push_back({false, c, L});
            types.push_back({true, c, L});
        }
    }
    std::map<Poly64, Entry> unique;
    Catalog result;
    std::vector<int> combo;
    auto visit = [&](const std::vector<int>& indices) {
        auto [adj, label] = build_bush(indices, types);
        if (adj.size() > 60) return;
        ++result.scanned;
        Poly64 p = indpoly_tree(adj);
        if (!unimodal64(p)) {
            ++result.single_hits;
            std::cerr << "UNEXPECTED_SINGLE_HIT " << label << "\n";
        }
        if (!logconcave(p) && !unique.count(p)) {
            unique.emplace(p, Entry{label, (int)adj.size(), p});
        }
    };
    for (int a = 2; a <= 5; ++a) {
        combo.assign(a, 0);
        auto rec = [&](auto&& self, int pos, int lo) -> void {
            if (pos == a) {
                visit(combo);
                return;
            }
            for (int i = lo; i < (int)types.size(); ++i) {
                combo[pos] = i;
                self(self, pos + 1, i);
            }
        };
        rec(rec, 0, 0);
    }
    result.entries.reserve(unique.size());
    // Public v2 star bushes add one vertex; published T* trees add two.
    // Merge the complete T_{3,m,n}/T*_{3,m,n} order<=60 supply.
    for (bool starred : {false, true}) {
        for (int m = 2; m <= 25; ++m) {
            for (int n = m; n <= 25; ++n) {
                auto [adj, label] = build_literature_tree(m, n, starred);
                if (adj.size() > 60) continue;
                Poly64 p = indpoly_tree(adj);
                if (!unimodal64(p)) {
                    ++result.single_hits;
                    std::cerr << "UNEXPECTED_SINGLE_HIT " << label << "\n";
                }
                if (!logconcave(p) && !unique.count(p))
                    unique.emplace(p, Entry{label, (int)adj.size(), p});
            }
        }
    }
    for (auto& [p, e] : unique) result.entries.push_back(std::move(e));
    return result;
}

static void dump_catalog(const std::vector<Entry>& entries, const std::string& path) {
    std::ofstream out(path, std::ios::binary);
    if (!out) throw std::runtime_error("cannot open catalog dump");
    for (std::size_t i = 0; i < entries.size(); ++i) {
        out << i << '\t' << entries[i].order << '\t' << entries[i].label << '\t';
        for (std::size_t k = 0; k < entries[i].poly.size(); ++k) {
            if (k) out << ',';
            out << entries[i].poly[k];
        }
        out << '\n';
    }
}

struct Hit {
    std::size_t i = 0, j = 0, valley = 0;
    std::vector<u128> product;
};

static bool product_unimodal(const Poly64& a, const Poly64& b,
                             std::array<u128, 128>& c,
                             std::size_t& len, std::size_t& valley) {
    len = a.size() + b.size() - 1;
    std::fill(c.begin(), c.begin() + len, (u128)0);
    for (std::size_t i = 0; i < a.size(); ++i)
        for (std::size_t j = 0; j < b.size(); ++j)
            c[i + j] += (u128)a[i] * b[j];
    bool falling = false;
    for (std::size_t k = 0; k + 1 < len; ++k) {
        if (c[k] > c[k + 1]) falling = true;
        else if (falling && c[k] < c[k + 1]) {
            valley = k;
            return false;
        }
    }
    return true;
}

int main(int argc, char** argv) {
    try {
        int threads = 1;
        bool catalog_only = false;
        std::string dump_path;
        for (int i = 1; i < argc; ++i) {
            std::string a = argv[i];
            if (a == "--threads" && i + 1 < argc) threads = std::stoi(argv[++i]);
            else if (a == "--catalog-only") catalog_only = true;
            else if (a == "--dump" && i + 1 < argc) dump_path = argv[++i];
            else throw std::runtime_error("bad argument: " + a);
        }
        if (threads < 1 || threads > 64) throw std::runtime_error("threads must be 1..64");
        auto t0 = std::chrono::steady_clock::now();
        Catalog catalog = generate_catalog();
        auto t1 = std::chrono::steady_clock::now();
        std::cout << "{\"phase\":\"catalog\",\"scanned\":" << catalog.scanned
                  << ",\"unique_non_lc\":" << catalog.entries.size()
                  << ",\"single_hits\":" << catalog.single_hits
                  << ",\"seconds\":"
                  << std::chrono::duration<double>(t1 - t0).count() << "}\n";
        if (!dump_path.empty()) dump_catalog(catalog.entries, dump_path);
        if (catalog.scanned != 112916 || catalog.entries.size() != 4499 ||
            catalog.single_hits != 0) {
            std::cerr << "FAILED: catalog invariant mismatch; refusing search\n";
            return 3;
        }

        if (catalog_only) return catalog.scanned == 112916 &&
                                 catalog.entries.size() == 4499 &&
                                 catalog.single_hits == 0 ? 0 : 3;

        const std::size_t n = catalog.entries.size();
        std::atomic<std::size_t> next_i{0};
        std::atomic<std::uint64_t> tested{0};
        std::atomic<bool> stop{false};
        std::mutex hit_mu;
        Hit hit;
        auto worker = [&]() {
            std::array<u128, 128> c{};
            std::uint64_t local = 0;
            while (!stop.load(std::memory_order_relaxed)) {
                std::size_t i = next_i.fetch_add(1);
                if (i >= n) break;
                for (std::size_t j = i; j < n; ++j) {
                    std::size_t len = 0, vk = 0;
                    if (!product_unimodal(catalog.entries[i].poly,
                                          catalog.entries[j].poly,
                                          c, len, vk)) {
                        bool expected = false;
                        if (stop.compare_exchange_strong(expected, true)) {
                            std::lock_guard<std::mutex> lock(hit_mu);
                            hit.i = i; hit.j = j; hit.valley = vk;
                            hit.product.assign(c.begin(), c.begin() + len);
                        }
                        break;
                    }
                    ++local;
                }
            }
            tested.fetch_add(local);
        };
        std::vector<std::thread> pool;
        for (int q = 0; q < threads; ++q) pool.emplace_back(worker);
        for (auto& th : pool) th.join();
        auto t2 = std::chrono::steady_clock::now();
        if (stop) {
            const auto& x = catalog.entries[hit.i];
            const auto& y = catalog.entries[hit.j];
            std::cout << "{\"status\":\"RAW_HIT\",\"i\":" << hit.i
                      << ",\"j\":" << hit.j
                      << ",\"valley_transition\":" << hit.valley
                      << ",\"label_i\":\"" << x.label
                      << "\",\"label_j\":\"" << y.label
                      << "\",\"product\":[";
            for (std::size_t k = 0; k < hit.product.size(); ++k) {
                if (k) std::cout << ',';
                std::cout << dec(hit.product[k]);
            }
            std::cout << "],\"tested_before_hit\":" << tested.load()
                      << ",\"seconds\":"
                      << std::chrono::duration<double>(t2 - t1).count() << "}\n";
            return 10;
        }
        std::uint64_t expected = (std::uint64_t)n * (n + 1) / 2;
        std::cout << "{\"status\":\"NO_HIT\",\"tested\":" << tested.load()
                  << ",\"expected\":" << expected
                  << ",\"threads\":" << threads
                  << ",\"seconds\":"
                  << std::chrono::duration<double>(t2 - t1).count() << "}\n";
        return tested.load() == expected ? 0 : 4;
    } catch (const std::exception& e) {
        std::cerr << "FAILED: " << e.what() << "\n";
        return 2;
    }
}
