#include <algorithm>
#include <array>
#include <atomic>
#include <bit>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <mutex>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace fs=std::filesystem;
static constexpr int N=26,COPIES=5;

struct Model{
    std::array<std::array<int,N>,N> edge_index{};
    std::vector<std::pair<uint8_t,uint8_t>> all_edges;
    std::vector<std::pair<uint8_t,uint8_t>> base_edges;
    std::array<std::vector<int>,N> base_neighbors;

    Model(){
        for(auto&r:edge_index)r.fill(-1);
        for(int u=0;u<N;++u)for(int v=u+1;v<N;++v){
            int e=static_cast<int>(all_edges.size());edge_index[u][v]=edge_index[v][u]=e;
            all_edges.push_back({static_cast<uint8_t>(u),static_cast<uint8_t>(v)});
        }
        std::array<int,11>part{};
        int z=0;for(int k=0;k<5;++k){int sz=k==0?3:2;for(int j=0;j<sz;++j)part[z++]=k;}
        for(int u=0;u<11;++u)for(int v=u+1;v<11;++v){
            int diff=(part[u]-part[v]+5)%5;
            bool f_edge=diff==1||diff==4;
            if(!f_edge)base_edges.push_back({static_cast<uint8_t>(u),static_cast<uint8_t>(v)});
        }
        for(int start:{11,16,21})for(int u=start;u<start+5;++u)for(int v=u+1;v<start+5;++v)
            base_edges.push_back({static_cast<uint8_t>(u),static_cast<uint8_t>(v)});
        if(base_edges.size()!=61)throw std::runtime_error("G61 edge count disagreement");
        for(auto[u,v]:base_edges){base_neighbors[u].push_back(v);base_neighbors[v].push_back(u);}
    }

    bool base_adjacent(int u,int v)const{
        return std::find(base_neighbors[u].begin(),base_neighbors[u].end(),v)!=base_neighbors[u].end();
    }
};

using Perm=std::array<uint8_t,N>;
struct Packing{
    std::array<Perm,COPIES>p{},inv{};
    std::array<uint8_t,325>count{},owners{};
    int overlap=0;
};

static bool valid_perm(const Perm&p){
    std::array<bool,N>seen{};
    for(uint8_t x:p){if(x>=N||seen[x])return false;seen[x]=true;}return true;
}
static int mapped_edge(const Model&m,const Perm&p,int u,int v){
    int a=p[u],b=p[v];if(a>b)std::swap(a,b);return m.edge_index[a][b];
}
static void rebuild(const Model&m,Packing&s){
    s.count.fill(0);s.owners.fill(0);s.overlap=0;
    for(int c=0;c<COPIES;++c){
        if(!valid_perm(s.p[c]))throw std::runtime_error("invalid permutation");
        for(int u=0;u<N;++u)s.inv[c][s.p[c][u]]=static_cast<uint8_t>(u);
        for(auto[u,v]:m.base_edges){
            int e=mapped_edge(m,s.p[c],u,v);
            if(s.owners[e]&(1u<<c))throw std::runtime_error("copy maps two base edges to one edge");
            s.owners[e]|=static_cast<uint8_t>(1u<<c);++s.count[e];
        }
    }
    for(uint8_t n:s.count)if(n>1)s.overlap+=n-1;
}

static std::vector<int> affected_base_edges(const Model&m,int a,int b){
    std::vector<int>ids;
    for(int i=0;i<static_cast<int>(m.base_edges.size());++i){
        auto[u,v]=m.base_edges[i];if(u==a||v==a||u==b||v==b)ids.push_back(i);
    }return ids;
}
struct SwapChange{std::vector<int>old_edges,new_edges,touched;int delta=0;};
static SwapChange evaluate_swap(const Model&m,const Packing&s,int c,int a,int b){
    if(c<=0||c>=COPIES||a==b)throw std::runtime_error("invalid movable swap");
    SwapChange ch;auto ids=affected_base_edges(m,a,b);Perm q=s.p[c];std::swap(q[a],q[b]);
    for(int id:ids){auto[u,v]=m.base_edges[id];
        ch.old_edges.push_back(mapped_edge(m,s.p[c],u,v));ch.new_edges.push_back(mapped_edge(m,q,u,v));}
    std::sort(ch.old_edges.begin(),ch.old_edges.end());
    ch.old_edges.erase(std::unique(ch.old_edges.begin(),ch.old_edges.end()),ch.old_edges.end());
    std::sort(ch.new_edges.begin(),ch.new_edges.end());
    ch.new_edges.erase(std::unique(ch.new_edges.begin(),ch.new_edges.end()),ch.new_edges.end());
    ch.touched=ch.old_edges;ch.touched.insert(ch.touched.end(),ch.new_edges.begin(),ch.new_edges.end());
    std::sort(ch.touched.begin(),ch.touched.end());ch.touched.erase(std::unique(ch.touched.begin(),ch.touched.end()),ch.touched.end());
    for(int e:ch.touched){
        bool old=std::binary_search(ch.old_edges.begin(),ch.old_edges.end(),e);
        bool neu=std::binary_search(ch.new_edges.begin(),ch.new_edges.end(),e);
        int before=s.count[e],after=before-static_cast<int>(old)+static_cast<int>(neu);
        ch.delta+=std::max(0,after-1)-std::max(0,before-1);
    }return ch;
}
static void apply_swap(const Model&m,Packing&s,int c,int a,int b,const SwapChange&ch){
    for(int e:ch.touched){
        bool old=std::binary_search(ch.old_edges.begin(),ch.old_edges.end(),e);
        bool neu=std::binary_search(ch.new_edges.begin(),ch.new_edges.end(),e);
        if(old&&!neu){--s.count[e];s.owners[e]&=static_cast<uint8_t>(~(1u<<c));}
        if(neu&&!old){++s.count[e];s.owners[e]|=static_cast<uint8_t>(1u<<c);}
    }
    int ta=s.p[c][a],tb=s.p[c][b];std::swap(s.p[c][a],s.p[c][b]);
    s.inv[c][ta]=static_cast<uint8_t>(b);s.inv[c][tb]=static_cast<uint8_t>(a);s.overlap+=ch.delta;
    (void)m;
}

static int sixset_alpha_violations(const Model&m){
    int bad=0;
    for(int a=0;a<N-5;++a)for(int b=a+1;b<N-4;++b)for(int c=b+1;c<N-3;++c)
    for(int d=c+1;d<N-2;++d)for(int e=d+1;e<N-1;++e)for(int f=e+1;f<N;++f){
        std::array<int,6>v{a,b,c,d,e,f};bool independent=true;
        for(int i=0;i<6&&independent;++i)for(int j=i+1;j<6;++j)
            if(m.base_adjacent(v[i],v[j])){independent=false;break;}
        if(independent)++bad;
    }return bad;
}

static void write_pack(const Packing&s,const fs::path&p){
    std::ofstream out(p);if(!out)throw std::runtime_error("cannot write pack");
    for(int c=0;c<COPIES;++c){for(int i=0;i<N;++i){if(i)out<<' ';out<<static_cast<int>(s.p[c][i]);}out<<'\n';}
}
static bool read_pack(const fs::path&p,Packing&s,std::string&error){
    std::ifstream in(p);if(!in){error="cannot open pack";return false;}std::string line;int c=0;
    while(std::getline(in,line)){if(line.empty()||line[0]=='#')continue;if(c>=COPIES){error="too many rows";return false;}
        std::istringstream row(line);for(int i=0;i<N;++i){int x;if(!(row>>x)||x<0||x>=N){error="bad permutation row";return false;}
            s.p[c][i]=static_cast<uint8_t>(x);}std::string extra;if(row>>extra){error="trailing token";return false;}++c;}
    if(c!=COPIES){error="expected five rows";return false;}for(const auto&q:s.p)if(!valid_perm(q)){error="row is not permutation";return false;}
    return true;
}

struct ColorVerification{uint64_t checked=0,missing=0;};
static std::vector<uint8_t> complete_coloring(const Model&m,const Packing&s){
    if(s.overlap)throw std::runtime_error("cannot color from overlapping packing");
    std::vector<uint8_t>color(325,255);
    for(int c=0;c<COPIES;++c)for(auto[u,v]:m.base_edges){
        int e=mapped_edge(m,s.p[c],u,v);if(color[e]!=255)throw std::runtime_error("packing overlap");color[e]=c;}
    for(int e=0;e<325;++e)if(color[e]==255)color[e]=static_cast<uint8_t>(e%5);
    return color;
}
static ColorVerification verify_coloring(const Model&m,const std::vector<uint8_t>&color){
    ColorVerification r;
    for(int a=0;a<N-5;++a)for(int b=a+1;b<N-4;++b)for(int c=b+1;c<N-3;++c)
    for(int d=c+1;d<N-2;++d)for(int e=d+1;e<N-1;++e)for(int f=e+1;f<N;++f){
        std::array<int,6>v{a,b,c,d,e,f};uint8_t present=0;
        for(int i=0;i<6;++i)for(int j=i+1;j<6;++j)present|=static_cast<uint8_t>(1u<<color[m.edge_index[v[i]][v[j]]]);
        r.missing+=std::popcount(static_cast<unsigned>((~present)&31u));++r.checked;
    }return r;
}
static void write_coloring(const Model&m,const std::vector<uint8_t>&color,const fs::path&p){
    std::ofstream out(p);if(!out)throw std::runtime_error("cannot write coloring");
    for(int e=0;e<325;++e)out<<static_cast<int>(m.all_edges[e].first)<<' '
        <<static_cast<int>(m.all_edges[e].second)<<' '<<static_cast<int>(color[e])<<'\n';
}

static Packing random_packing(std::mt19937_64&rng){
    Packing s;for(int c=0;c<COPIES;++c){std::iota(s.p[c].begin(),s.p[c].end(),0);
        if(c)std::shuffle(s.p[c].begin(),s.p[c].end(),rng);}return s;
}
static bool audit(const Model&m,const fs::path&dir,std::string&why){
    fs::create_directories(dir);
    if(sixset_alpha_violations(m)!=0){why="G61 has an independent six-set";return false;}
    // Exact clique audit only needs six-subsets; max clique at least five is explicit.
    int clique6=0;
    for(int a=0;a<N-5;++a)for(int b=a+1;b<N-4;++b)for(int c=b+1;c<N-3;++c)
    for(int d=c+1;d<N-2;++d)for(int e=d+1;e<N-1;++e)for(int f=e+1;f<N;++f){
        std::array<int,6>v{a,b,c,d,e,f};bool clique=true;
        for(int i=0;i<6&&clique;++i)for(int j=i+1;j<6;++j)if(!m.base_adjacent(v[i],v[j])){clique=false;break;}
        if(clique)++clique6;
    }
    if(clique6){why="G61 has a K6";return false;}
    Packing repeated;for(int c=0;c<COPIES;++c)std::iota(repeated.p[c].begin(),repeated.p[c].end(),0);rebuild(m,repeated);
    if(repeated.overlap!=244){why="repeated-copy objective not 244";return false;}
    write_pack(repeated,dir/"repeated_identity.pack");
    std::string error;Packing parsed;if(!read_pack(dir/"repeated_identity.pack",parsed,error)){why="canonical parser rejected fixture";return false;}
    rebuild(m,parsed);if(parsed.overlap!=244){why="parsed objective mismatch";return false;}
    std::mt19937_64 rng(6176102ULL);Packing s=random_packing(rng);rebuild(m,s);
    for(int k=0;k<2000;++k){
        int c=1+rng()%4,a=rng()%N,b;do{b=rng()%N;}while(a==b);
        int before=s.overlap;auto ch=evaluate_swap(m,s,c,a,b);Packing copy=s;apply_swap(m,copy,c,a,b,ch);
        Packing exact=copy;rebuild(m,exact);
        if(copy.overlap!=exact.overlap||copy.count!=exact.count||copy.owners!=exact.owners||
           copy.overlap-before!=ch.delta){why="incremental swap disagreement at "+std::to_string(k);return false;}
        s=std::move(copy);
    }
    std::ofstream bad(dir/"corrupt_duplicate_value.pack");
    for(int c=0;c<5;++c){for(int i=0;i<26;++i){if(i)bad<<' ';bad<<(c==0&&i==25?24:i);}bad<<'\n';}bad.close();
    if(read_pack(dir/"corrupt_duplicate_value.pack",parsed,error)){why="parser accepted non-permutation";return false;}
    return true;
}

struct Shared{std::atomic<bool>stop{false};std::atomic<int>best{999};std::atomic<uint64_t>moves{0};
    std::mutex mutex;fs::path out;std::chrono::steady_clock::time_point deadline;};
static void publish(const Packing&s,Shared&sh,int worker,uint64_t moves){
    int old=sh.best.load();while(s.overlap<old&&!sh.best.compare_exchange_weak(old,s.overlap)){}
    if(s.overlap<=sh.best.load()){
        std::lock_guard<std::mutex>lock(sh.mutex);
        if(s.overlap!=sh.best.load())return;
        write_pack(s,sh.out/"best_checkpoint.pack");
        std::ofstream meta(sh.out/"best_checkpoint.txt");
        meta<<"worker "<<worker<<"\nmoves "<<moves<<"\noverlap "<<s.overlap<<"\n";
    }
}
static void worker(const Model&m,Shared&sh,int id,uint64_t seed){
    std::mt19937_64 rng(seed+0x9e3779b97f4a7c15ULL*(id+1));uint64_t moves=0;
    while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline){
        Packing s=random_packing(rng);rebuild(m,s);publish(s,sh,id,moves);int local=s.overlap;uint64_t improved=moves;
        std::array<std::array<uint64_t,N>,COPIES>tabu{};
        while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline&&moves-improved<100000){
            if(!s.overlap){auto color=complete_coloring(m,s);auto vr=verify_coloring(m,color);
                if(vr.missing)throw std::runtime_error("zero packing failed full verifier");
                {std::lock_guard<std::mutex>lock(sh.mutex);write_pack(s,sh.out/"verified_hit.pack");
                 write_coloring(m,color,sh.out/"verified_hit.col");std::ofstream rep(sh.out/"verified_hit_g61_b.txt");
                 rep<<"status VERIFIED_HIT\nworker "<<id<<"\nmoves "<<moves<<"\noverlap 0\nleftover_edges 20\n"
                    <<"subsets_checked "<<vr.checked<<"\nmissing_pairs "<<vr.missing<<"\n";}
                sh.best.store(0);sh.stop.store(true);return;}
            std::vector<int>dup;for(int e=0;e<325;++e)if(s.count[e]>1)dup.push_back(e);
            if(dup.empty())throw std::runtime_error("positive overlap without duplicate edge");
            int target=dup[rng()%dup.size()];uint8_t mask=s.owners[target];int movable[5],nm=0;
            for(int c=1;c<5;++c)if(mask&(1u<<c))movable[nm++]=c;
            if(!nm){target=dup[rng()%dup.size()];for(int c=1;c<5;++c)if(s.owners[target]&(1u<<c))movable[nm++]=c;}
            if(!nm)continue;int c=movable[rng()%nm];auto[x,y]=m.all_edges[target];int a=s.inv[c][x],b=s.inv[c][y];
            int bestd=999,ca[52],cb[52],nc=0;
            for(int endpoint:{a,b})for(int z=0;z<N;++z)if(z!=endpoint){
                auto ch=evaluate_swap(m,s,c,endpoint,z);bool is_tabu=tabu[c][endpoint]>moves||tabu[c][z]>moves;
                if(is_tabu&&s.overlap+ch.delta>=sh.best.load())continue;
                if(ch.delta<bestd){bestd=ch.delta;nc=0;ca[nc]=endpoint;cb[nc++]=z;}
                else if(ch.delta==bestd){ca[nc]=endpoint;cb[nc++]=z;}}
            if(!nc){int z;do{z=rng()%N;}while(z==a);ca[0]=a;cb[0]=z;nc=1;}
            int pick=rng()%nc;if(rng()%100<8){ca[pick]=rng()%N;do{cb[pick]=rng()%N;}while(cb[pick]==ca[pick]);}
            auto ch=evaluate_swap(m,s,c,ca[pick],cb[pick]);apply_swap(m,s,c,ca[pick],cb[pick],ch);
            tabu[c][ca[pick]]=tabu[c][cb[pick]]=moves+3+rng()%23;++moves;
            if(s.overlap<local){local=s.overlap;improved=moves;publish(s,sh,id,moves);}
            if((moves&4095u)==0){Packing exact=s;rebuild(m,exact);if(exact.overlap!=s.overlap||exact.count!=s.count)
                throw std::runtime_error("periodic packing audit failed");sh.moves.fetch_add(4096);}
            if(moves-improved>10000&&moves%128==0){int cc=1+rng()%4,a0=rng()%N,b0;do{b0=rng()%N;}while(a0==b0);
                auto shake=evaluate_swap(m,s,cc,a0,b0);apply_swap(m,s,cc,a0,b0,shake);}
        }
    }sh.moves.fetch_add(moves&4095u);
}

int main(int argc,char**argv){
    try{Model m;
        if(argc==3&&std::string(argv[1])=="--selftest"){std::string why;if(!audit(m,argv[2],why)){
            std::cerr<<"SELFTEST FAIL "<<why<<"\n";return 1;}
            std::cout<<"SELFTEST PASS\nbase_vertices 26\nbase_edges 61\nbase_independent6 0\nbase_clique6 0\n"
                <<"repeated_identity_overlap 244\nincremental_swap_audits 2000\nparser_corruptions_rejected 1\n";return 0;}
        if(argc==4&&std::string(argv[1])=="--verify-pack"){Packing s;std::string error;if(!read_pack(argv[3],s,error)){
            std::cout<<"status PARSE_REJECT\nerror "<<error<<"\n";return 1;}rebuild(m,s);
            std::cout<<"status "<<(s.overlap?"OVERLAP":"DISJOINT")<<"\noverlap "<<s.overlap
                <<"\nunion_edges "<<305-s.overlap<<"\n";return s.overlap?1:0;}
        if(argc==6&&std::string(argv[1])=="--search"){
            int threads=std::stoi(argv[2]),seconds=std::stoi(argv[3]);uint64_t seed=std::stoull(argv[4]);
            if(threads<1||threads>64||seconds<1)throw std::runtime_error("bad args");Shared sh;sh.out=argv[5];
            fs::create_directories(sh.out);sh.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(seconds);
            std::vector<std::thread>pool;for(int i=0;i<threads;++i)pool.emplace_back(worker,std::cref(m),std::ref(sh),i,seed);
            auto next=std::chrono::steady_clock::now()+std::chrono::seconds(5);
            while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline){
                std::this_thread::sleep_for(std::chrono::milliseconds(100));if(std::chrono::steady_clock::now()>=next){
                    std::cout<<"best_overlap "<<sh.best.load()<<" moves "<<sh.moves.load()<<"\n";next+=std::chrono::seconds(5);}}
            sh.stop.store(true);for(auto&t:pool)t.join();int best=sh.best.load();std::ofstream sum(sh.out/"summary.txt");
            sum<<"status "<<(best==0?"VERIFIED_HIT":"NO_HIT")<<"\nthreads "<<threads<<"\nseconds "<<seconds
                <<"\nseed "<<seed<<"\nbest_overlap "<<best<<"\ntotal_moves "<<sh.moves.load()<<"\n";
            std::cout<<"FINAL "<<(best==0?"VERIFIED_HIT":"NO_HIT")<<" best_overlap "<<best
                <<" moves "<<sh.moves.load()<<"\n";return best==0?0:3;}
        std::cerr<<"Usage: --selftest DIR | --verify-pack N FILE | --search THREADS SECONDS SEED OUTDIR\n";return 2;
    }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}
}
