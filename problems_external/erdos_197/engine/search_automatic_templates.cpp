#include <algorithm>
#include <atomic>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <tuple>
#include <vector>
using namespace std;

struct ColourDesc { int type, period, mask, toggle; };
struct OrderDesc { int transform[2], mask_id[2], alt[2]; };
struct Trial { int colour_id, order_id, passed_bits, wx, wy, wz; };

static uint64_t width_mask(int w) { return w == 64 ? ~0ULL : ((1ULL << w) - 1); }
static uint64_t reverse_bits(uint64_t x, int w) {
    uint64_t y=0; for(int i=0;i<w;++i) y=(y<<1)|((x>>i)&1ULL); return y;
}
static uint64_t inverse_gray(uint64_t g) {
    uint64_t x=0; for(;g;g>>=1) x^=g; return x;
}
static uint64_t transform_key(uint64_t x, int w, int t) {
    uint64_t y=x;
    if(t==1) y=reverse_bits(x,w);
    else if(t==2) y=x^(x>>1);
    else if(t==3) y=reverse_bits(x^(x>>1),w);
    else if(t==4) y=inverse_gray(x);
    else if(t==5) y=reverse_bits(inverse_gray(x),w);
    return y & width_mask(w);
}
static uint64_t pattern_mask(int w, int id) {
    uint64_t m=0;
    for(int j=0;j<w;++j) {
        bool on=false;
        if(id==1) on=true;
        else if(id==2) on=(j%2==0);
        else if(id==3) on=(j%2==1);
        else if(id>=4 && id<=6) on=(j%3==id-4);
        if(on) m|=1ULL<<j;
    }
    return m;
}
static int colour_of(uint64_t x, int w, const ColourDesc& d) {
    int ans=0;
    if(d.type==0 || d.type==1) {
        for(int j=0;j<w;++j) if((x>>j)&1ULL) {
            int r=d.type==0 ? j%d.period : (w-1-j)%d.period;
            if((d.mask>>r)&1) ans^=1;
        }
        if(d.toggle && (w&1)) ans^=1;
    } else if(d.type==2) {
        int v=countr_zero(x)%d.period; ans=(d.mask>>v)&1;
    } else {
        int r=w%d.period; ans=(d.mask>>r)&1;
    }
    return ans;
}
struct Item { uint8_t c,w; uint64_t key; };
static bool before(const Item& a,const Item& b) {
    return a.w!=b.w ? a.w<b.w : a.key<b.key;
}
static bool check_prefix(int bits,const ColourDesc& cd,const OrderDesc& od,int& wx,int& wy,int& wz) {
    const int n=(1<<bits)-1;
    vector<Item> a(n+1);
    for(int x=1;x<=n;++x) {
        int w=bit_width((unsigned)x), c=colour_of(x,w,cd);
        uint64_t k=transform_key(x,w,od.transform[c]);
        k^=pattern_mask(w,od.mask_id[c]);
        if(od.alt[c] && (w&1)) k^=width_mask(w);
        a[x]={(uint8_t)c,(uint8_t)w,k};
    }
    for(int x=1;x<=n;++x) for(int d=1;x+2*d<=n;++d) {
        int y=x+d,z=x+2*d;
        if(a[x].c!=a[y].c || a[x].c!=a[z].c) continue;
        if((before(a[x],a[y])&&before(a[y],a[z])) || (before(a[z],a[y])&&before(a[y],a[x]))) {
            wx=x;wy=y;wz=z;return false;
        }
    }
    return true;
}
static vector<ColourDesc> make_colours() {
    vector<ColourDesc> v;
    for(int type=0;type<=1;++type) for(int p=1;p<=5;++p) for(int mask=1;mask<(1<<p);++mask)
        for(int toggle=0;toggle<=1;++toggle) v.push_back({type,p,mask,toggle});
    for(int type=2;type<=3;++type) for(int p=2;p<=5;++p) for(int mask=1;mask<(1<<p)-1;++mask)
        v.push_back({type,p,mask,0});
    return v;
}
static vector<OrderDesc> make_orders() {
    vector<OrderDesc> v;
    for(int t0=0;t0<6;++t0) for(int t1=0;t1<6;++t1)
    for(int m0=0;m0<7;++m0) for(int m1=0;m1<7;++m1)
    for(int a0=0;a0<2;++a0) for(int a1=0;a1<2;++a1) v.push_back({{t0,t1},{m0,m1},{a0,a1}});
    return v;
}
static void write_cert(const string& path,int bits,const ColourDesc& cd,const OrderDesc& od) {
    int n=(1<<bits)-1; vector<pair<uint64_t,int>> s[2];
    for(int x=1;x<=n;++x) {
        int w=bit_width((unsigned)x),c=colour_of(x,w,cd);
        uint64_t k=transform_key(x,w,od.transform[c])^pattern_mask(w,od.mask_id[c]);
        if(od.alt[c]&&(w&1)) k^=width_mask(w);
        uint64_t composite=(uint64_t(w)<<56)|k; s[c].push_back({composite,x});
    }
    for(auto& q:s) sort(q.begin(),q.end());
    ofstream f(path); f<<n<<'\n';
    for(int c=0;c<2;++c) { f<<s[c].size(); for(auto [k,x]:s[c]) f<<' '<<x; f<<'\n'; }
}
int main(int argc,char** argv) {
    int threads=1,max_bits=10; string cert="best_candidate.txt";
    for(int i=1;i<argc;++i) {
        string a=argv[i];
        if(a=="--threads"&&i+1<argc) threads=stoi(argv[++i]);
        else if(a=="--max-bits"&&i+1<argc) max_bits=stoi(argv[++i]);
        else if(a=="--cert"&&i+1<argc) cert=argv[++i];
        else { cerr<<"bad argument: "<<a<<'\n'; return 2; }
    }
    if(threads<1||threads>64||max_bits<3||max_bits>20) return 2;
    auto colours=make_colours(); auto orders=make_orders();
    uint64_t total=(uint64_t)colours.size()*orders.size(); atomic<uint64_t> next{0};
    mutex mu; Trial best{-1,-1,2,0,0,0}; atomic<uint64_t> tested{0};
    auto worker=[&]() {
        Trial local_best{-1,-1,2,0,0,0};
        for(;;) {
            uint64_t id=next.fetch_add(1); if(id>=total) break;
            int ci=(int)(id/orders.size()),oi=(int)(id%orders.size()); int wx=0,wy=0,wz=0,passed=2;
            for(int b=3;b<=max_bits;++b) { if(!check_prefix(b,colours[ci],orders[oi],wx,wy,wz)) break; passed=b; }
            if(passed>local_best.passed_bits) local_best={ci,oi,passed,wx,wy,wz};
            tested.fetch_add(1,memory_order_relaxed);
        }
        lock_guard<mutex> lock(mu); if(local_best.passed_bits>best.passed_bits) best=local_best;
    };
    vector<thread> pool; for(int i=0;i<threads;++i) pool.emplace_back(worker); for(auto& t:pool)t.join();
    const auto& cd=colours[best.colour_id]; const auto& od=orders[best.order_id];
    write_cert(cert,best.passed_bits,cd,od);
    cout<<"{\"status\":\"COMPLETE\",\"templates\":"<<tested.load()<<",\"colour_count\":"<<colours.size()
        <<",\"order_count\":"<<orders.size()<<",\"best_bits\":"<<best.passed_bits<<",\"best_n\":"<<((1<<best.passed_bits)-1)
        <<",\"colour_id\":"<<best.colour_id<<",\"order_id\":"<<best.order_id
        <<",\"colour\":["<<cd.type<<','<<cd.period<<','<<cd.mask<<','<<cd.toggle<<"]"
        <<",\"order\":["<<od.transform[0]<<','<<od.transform[1]<<','<<od.mask_id[0]<<','<<od.mask_id[1]<<','<<od.alt[0]<<','<<od.alt[1]<<"]"
        <<",\"next_witness\":["<<best.wx<<','<<best.wy<<','<<best.wz<<"],\"cert\":\""<<cert<<"\"}\n";
}
