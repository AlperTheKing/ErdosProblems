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
#include <map>
#include <mutex>
#include <random>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace fs=std::filesystem;
static constexpr int N=26,D=12,Q=5;

struct Clause{std::array<uint8_t,D> mask{};};

struct Model{
    std::array<std::array<int,N>,N> edge_index{};
    std::vector<std::pair<uint8_t,uint8_t>> edges;
    std::array<std::array<int,5>,5> direction{};
    std::array<int,325> edge_dir{},edge_mid{};
    std::vector<Clause> clauses;
    std::array<std::array<std::vector<uint32_t>,Q>,D> incidence;

    Model(){
        for(auto&r:edge_index)r.fill(-1);
        for(auto&r:direction)r.fill(-1);
        for(int u=0;u<N;++u)for(int v=u+1;v<N;++v){
            int e=static_cast<int>(edges.size());edge_index[u][v]=edge_index[v][u]=e;
            edges.push_back({static_cast<uint8_t>(u),static_cast<uint8_t>(v)});
        }
        std::map<std::pair<int,int>,int> ids;
        for(int dx=0;dx<5;++dx)for(int dy=0;dy<5;++dy)if(dx||dy){
            std::pair<int,int>a{dx,dy},b{(5-dx)%5,(5-dy)%5};
            auto canon=std::min(a,b);
            if(!ids.count(canon)){int z=static_cast<int>(ids.size());ids[canon]=z;}
            direction[dx][dy]=ids[canon];
        }
        if(ids.size()!=12)throw std::runtime_error("expected 12 unoriented directions");
        std::array<int,D> dir_edges{};
        for(int e=0;e<325;++e){
            int u=edges[e].first,v=edges[e].second;
            if(v==25){edge_dir[e]=-1;edge_mid[e]=u%5;continue;}
            int x1=u%5,y1=u/5,x2=v%5,y2=v/5;
            int dx=(x2-x1+5)%5,dy=(y2-y1+5)%5;
            edge_dir[e]=direction[dx][dy];
            edge_mid[e]=((x1+x2)*3)%5;
            ++dir_edges[edge_dir[e]];
        }
        for(int z:dir_edges)if(z!=25)throw std::runtime_error("direction does not have 25 edges");

        for(int a=0;a<N-5;++a)for(int b=a+1;b<N-4;++b)for(int c=b+1;c<N-3;++c)
        for(int d=c+1;d<N-2;++d)for(int e=d+1;e<N-1;++e)for(int f=e+1;f<N;++f){
            std::array<int,6>vv{a,b,c,d,e,f};bool fixed_zero=false;Clause cl;
            for(int i=0;i<6;++i)for(int j=i+1;j<6;++j){
                int ge=edge_index[vv[i]][vv[j]];
                if(edge_dir[ge]<0){if(edge_mid[ge]==0)fixed_zero=true;}
                else{
                    int need=(5-edge_mid[ge])%5;
                    cl.mask[edge_dir[ge]]|=static_cast<uint8_t>(1u<<need);
                }
            }
            if(!fixed_zero)clauses.push_back(cl);
        }
        if(clauses.size()!=192604)throw std::runtime_error("unexpected residual clause count");
        for(uint32_t q=0;q<clauses.size();++q)for(int d=0;d<D;++d)
            for(int h=0;h<Q;++h)if(clauses[q].mask[d]&(1u<<h))incidence[d][h].push_back(q);
    }

    std::vector<uint8_t> colors(const std::array<uint8_t,D>&h)const{
        std::vector<uint8_t>c(325);
        for(int e=0;e<325;++e)c[e]=edge_dir[e]<0?static_cast<uint8_t>(edge_mid[e]):
            static_cast<uint8_t>((edge_mid[e]+h[edge_dir[e]])%5);
        return c;
    }

    void write_raw(const std::array<uint8_t,D>&h,const fs::path&p)const{
        auto c=colors(h);std::ofstream out(p);if(!out)throw std::runtime_error("cannot write certificate");
        for(int e=0;e<325;++e)out<<static_cast<int>(edges[e].first)<<' '
            <<static_cast<int>(edges[e].second)<<' '<<static_cast<int>(c[e])<<'\n';
    }
};

struct FullResult{uint64_t checked=0,missing=0;};
static FullResult full_verify(const Model&m,const std::array<uint8_t,D>&h){
    auto color=m.colors(h);FullResult r;
    for(int a=0;a<N-5;++a)for(int b=a+1;b<N-4;++b)for(int c=b+1;c<N-3;++c)
    for(int d=c+1;d<N-2;++d)for(int e=d+1;e<N-1;++e)for(int f=e+1;f<N;++f){
        std::array<int,6>vv{a,b,c,d,e,f};uint8_t present=0;
        for(int i=0;i<6;++i)for(int j=i+1;j<6;++j)
            present|=static_cast<uint8_t>(1u<<color[m.edge_index[vv[i]][vv[j]]]);
        r.missing+=std::popcount(static_cast<unsigned>((~present)&31u));++r.checked;
    }return r;
}

struct State{
    std::array<uint8_t,D>h{};
    std::vector<uint8_t>count;
    std::vector<int32_t>bad_pos;
    std::vector<uint32_t>bad;
    int score=0;
};
static void add_bad(State&s,uint32_t q){if(s.bad_pos[q]>=0)return;s.bad_pos[q]=s.bad.size();s.bad.push_back(q);}
static void rem_bad(State&s,uint32_t q){int p=s.bad_pos[q];if(p<0)return;uint32_t z=s.bad.back();
    s.bad[p]=z;s.bad_pos[z]=p;s.bad.pop_back();s.bad_pos[q]=-1;}
static void rebuild(const Model&m,State&s){
    s.count.assign(m.clauses.size(),0);s.bad_pos.assign(m.clauses.size(),-1);s.bad.clear();s.score=0;
    for(uint32_t q=0;q<m.clauses.size();++q){
        for(int d=0;d<D;++d)if(m.clauses[q].mask[d]&(1u<<s.h[d]))++s.count[q];
        if(!s.count[q]){++s.score;add_bad(s,q);}
    }
}
static int delta(const Model&m,const State&s,int d,uint8_t target){
    uint8_t old=s.h[d];if(old==target)return 0;int change=0;
    for(uint32_t q:m.incidence[d][old]){
        bool target_also=m.clauses[q].mask[d]&(1u<<target);
        if(!target_also&&s.count[q]==1)++change;
    }
    for(uint32_t q:m.incidence[d][target]){
        bool old_also=m.clauses[q].mask[d]&(1u<<old);
        if(!old_also&&s.count[q]==0)--change;
    }return change;
}
static void apply(const Model&m,State&s,int d,uint8_t target){
    uint8_t old=s.h[d];if(old==target)return;int change=0;
    for(uint32_t q:m.incidence[d][old]){
        bool new_also=m.clauses[q].mask[d]&(1u<<target);
        if(new_also)continue;
        if(s.count[q]==1){++change;add_bad(s,q);}--s.count[q];
    }
    for(uint32_t q:m.incidence[d][target]){
        bool old_also=m.clauses[q].mask[d]&(1u<<old);
        if(old_also)continue;
        if(s.count[q]==0){--change;rem_bad(s,q);}++s.count[q];
    }
    s.h[d]=target;s.score+=change;
}
static int reduced_score(const Model&m,const std::array<uint8_t,D>&h){State s;s.h=h;rebuild(m,s);return s.score;}

static bool audit(const Model&m,std::string&why){
    std::mt19937_64 rng(6171202ULL);
    for(int t=0;t<20;++t){
        State s;for(auto&x:s.h)x=static_cast<uint8_t>(rng()%5);rebuild(m,s);
        auto full=full_verify(m,s.h);
        if(full.checked!=230230||full.missing!=5ull*static_cast<uint64_t>(s.score)){
            why="full/reduced covariance mismatch";return false;}
        auto colors=m.colors(s.h);std::array<int,5>sizes{};
        for(uint8_t c:colors)++sizes[c];for(int z:sizes)if(z!=65){why="color size not 65";return false;}
        for(int shift=0;shift<5;++shift)for(int e=0;e<325;++e){
            int u=m.edges[e].first,v=m.edges[e].second;
            int tu=u==25?25:(u/5)*5+(u%5+shift)%5;
            int tv=v==25?25:(v/5)*5+(v%5+shift)%5;
            if(tu>tv)std::swap(tu,tv);
            if(colors[m.edge_index[tu][tv]]!=(colors[e]+shift)%5){why="translation covariance failed";return false;}
        }
    }
    State s;for(auto&x:s.h)x=static_cast<uint8_t>(rng()%5);rebuild(m,s);
    for(int k=0;k<500;++k){int d=rng()%D;uint8_t h;do{h=rng()%5;}while(h==s.h[d]);
        int before=s.score,pred=delta(m,s,d,h);apply(m,s,d,h);int exact=reduced_score(m,s.h);
        auto full=full_verify(m,s.h);
        if(s.score!=exact||exact-before!=pred||full.missing!=5ull*exact){
            why="incremental delta audit mismatch";return false;}}
    return true;
}

struct Shared{std::atomic<bool>stop{false};std::atomic<int>best{std::numeric_limits<int>::max()};
    std::atomic<uint64_t>moves{0};std::mutex mutex;fs::path out;std::chrono::steady_clock::time_point deadline;};
static void publish(const Model&m,Shared&sh,const State&s,int worker,uint64_t moves){
    int old=sh.best.load();while(s.score<old&&!sh.best.compare_exchange_weak(old,s.score)){}
    if(s.score<=sh.best.load()){std::lock_guard<std::mutex>lock(sh.mutex);m.write_raw(s.h,sh.out/"best_checkpoint.col");
        std::ofstream meta(sh.out/"best_checkpoint.txt");meta<<"worker "<<worker<<"\nmoves "<<moves
            <<"\nmissing_sixsets_color0 "<<s.score<<"\nfull_missing_pairs "<<5*s.score<<"\noffsets";
        for(auto x:s.h)meta<<' '<<static_cast<int>(x);meta<<'\n';}}
static void worker(const Model&m,Shared&sh,int id,uint64_t seed){
    std::mt19937_64 rng(seed+0x9e3779b97f4a7c15ULL*(id+1));uint64_t moves=0;int restart=0;
    while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline){
        State s;for(auto&x:s.h)x=static_cast<uint8_t>(rng()%5);rebuild(m,s);publish(m,sh,s,id,moves);
        int local=s.score;uint64_t improve=moves;std::array<uint64_t,D>tabu{};
        while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline&&moves-improve<10000){
            if(s.score==0){auto full=full_verify(m,s.h);if(full.missing)throw std::runtime_error("hit replay disagreement");
                {std::lock_guard<std::mutex>lock(sh.mutex);m.write_raw(s.h,sh.out/"verified_hit.col");
                 std::ofstream rep(sh.out/"verified_hit_covariant_b.txt");rep<<"status VERIFIED_HIT\nworker "<<id
                 <<"\nmoves "<<moves<<"\nsubsets_checked "<<full.checked<<"\nmissing_pairs "<<full.missing<<"\noffsets";
                 for(auto x:s.h)rep<<' '<<static_cast<int>(x);rep<<'\n';}
                sh.best.store(0);sh.stop.store(true);return;}
            uint32_t q=s.bad[rng()%s.bad.size()];int candD[60],candH[60],nc=0,bestd=std::numeric_limits<int>::max();
            for(int d=0;d<D;++d)for(int h=0;h<5;++h)if(m.clauses[q].mask[d]&(1u<<h)){
                if(h==s.h[d])continue;int de=delta(m,s,d,h);
                if(tabu[d]>moves&&s.score+de>=sh.best.load())continue;
                if(de<bestd){bestd=de;nc=0;candD[nc]=d;candH[nc++]=h;}
                else if(de==bestd){candD[nc]=d;candH[nc++]=h;}}
            if(!nc)throw std::runtime_error("violated clause has no repair");
            int z=rng()%nc;if(rng()%100<8){z=rng()%nc;}
            apply(m,s,candD[z],static_cast<uint8_t>(candH[z]));tabu[candD[z]]=moves+2+rng()%9;++moves;
            if(s.score<local){local=s.score;improve=moves;publish(m,sh,s,id,moves);}
            if((moves&255u)==0){int exact=reduced_score(m,s.h);if(exact!=s.score)throw std::runtime_error("score disagreement");
                sh.moves.fetch_add(256);}
            if(moves-improve>2000&&moves%64==0){int d=rng()%D;uint8_t h=rng()%5;if(h!=s.h[d])apply(m,s,d,h);}
        }++restart;
    }sh.moves.fetch_add(moves&255u);
}

int main(int argc,char**argv){
    try{Model m;
        if(argc==2&&std::string(argv[1])=="--selftest"){std::string why;if(!audit(m,why)){
            std::cerr<<"SELFTEST FAIL "<<why<<"\n";return 1;}
            std::cout<<"SELFTEST PASS\ndirections 12\nedges_per_direction 25\nresidual_color0_clauses 192604\n"
                <<"random_full_covariance_replays 20\nincremental_delta_replays 500\n"
                <<"color_class_size 65\nfull_sixsets 230230\n";return 0;}
        if(argc==6&&std::string(argv[1])=="--search"){
            int threads=std::stoi(argv[2]),seconds=std::stoi(argv[3]);uint64_t seed=std::stoull(argv[4]);
            if(threads<1||threads>63||seconds<1)throw std::runtime_error("bad args");
            std::string why;if(!audit(m,why))throw std::runtime_error("audit "+why);
            Shared sh;sh.out=argv[5];fs::create_directories(sh.out);
            sh.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(seconds);
            std::vector<std::thread>pool;for(int i=0;i<threads;++i)pool.emplace_back(worker,std::cref(m),std::ref(sh),i,seed);
            auto next=std::chrono::steady_clock::now()+std::chrono::seconds(5);
            while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline){
                std::this_thread::sleep_for(std::chrono::milliseconds(100));if(std::chrono::steady_clock::now()>=next){
                    std::cout<<"best_color0 "<<sh.best.load()<<" full_missing "<<5*sh.best.load()
                        <<" moves "<<sh.moves.load()<<"\n";next+=std::chrono::seconds(5);}}
            sh.stop.store(true);for(auto&t:pool)t.join();int best=sh.best.load();
            std::ofstream sum(sh.out/"summary.txt");sum<<"status "<<(best==0?"VERIFIED_HIT":"NO_HIT")
                <<"\nthreads "<<threads<<"\nseconds "<<seconds<<"\nseed "<<seed
                <<"\nbest_color0_missing "<<best<<"\nbest_full_missing_pairs "<<5*best
                <<"\ntotal_moves "<<sh.moves.load()<<"\n";
            std::cout<<"FINAL "<<(best==0?"VERIFIED_HIT":"NO_HIT")<<" best_color0 "<<best
                <<" full_missing "<<5*best<<" moves "<<sh.moves.load()<<"\n";return best==0?0:3;}
        std::cerr<<"Usage: --selftest | --search THREADS SECONDS SEED OUT_DIR\n";return 2;
    }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}
}
