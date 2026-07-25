#define main erdos617_native_b_embedded_main
#include "erdos617_native_b.cpp"
#undef main

static std::vector<uint8_t> singleton_slope_seed(const Instance &g, std::mt19937_64 &rng) {
    std::vector<uint8_t> colors(g.edge_count, 0);
    for (int e = 0; e < g.edge_count; ++e) {
        auto [u0,v0] = g.endpoints[e];
        int u=u0,v=v0;
        if (v==25 || u%5==v%5) {
            colors[e]=static_cast<uint8_t>(rng()%5);
        } else {
            int dx=(v%5-u%5+5)%5, dy=(v/5-u/5+5)%5;
            colors[e]=static_cast<uint8_t>((dy*inv5(dx))%5);
        }
    }
    return colors;
}

static std::vector<uint8_t> balanced_random_seed(const Instance &g, std::mt19937_64 &rng) {
    std::vector<uint8_t> colors(g.edge_count);
    for(int e=0;e<g.edge_count;++e) colors[e]=static_cast<uint8_t>(e%5);
    std::shuffle(colors.begin(),colors.end(),rng);
    return colors;
}

static std::vector<uint8_t> allowed_star(const Instance &g) {
    std::vector<uint8_t> a(g.edge_count,0);
    for(int u=0;u<25;++u) a[g.edge_index[u][25]]=1;
    return a;
}

static std::vector<uint8_t> allowed_vertical_star(const Instance &g) {
    auto a=allowed_star(g);
    for(int u=0;u<25;++u) for(int v=u+1;v<25;++v) if(u%5==v%5) a[g.edge_index[u][v]]=1;
    return a;
}

static void restricted_improve(const Instance &g, State &st, const std::vector<uint8_t> &allowed,
                               std::mt19937_64 &rng, int moves) {
    rebuild(g,st);
    int best=st.score, stale=0;
    for(int iter=0;iter<moves && st.score>0;++iter) {
        if(st.bad_sets.empty()) throw std::runtime_error("positive score with no bad sets");
        uint32_t s=st.bad_sets[rng()%st.bad_sets.size()];
        uint8_t mm=st.missing_mask[s];
        int opts[5],no=0;
        for(int c=0;c<5;++c) if(mm&(1u<<c)) opts[no++]=c;
        uint8_t target=static_cast<uint8_t>(opts[rng()%no]);
        int cand[15],nc=0,bestd=std::numeric_limits<int>::max();
        for(uint16_t e:g.six_edges[s]) {
            if(!allowed[e]||st.colors[e]==target) continue;
            int d=delta_recolor(g,st,e,target);
            if(d<bestd){bestd=d;nc=0;cand[nc++]=e;}
            else if(d==bestd)cand[nc++]=e;
        }
        if(nc==0) break;
        int e=(rng()%100<5)?cand[rng()%nc]:cand[rng()%nc];
        apply_recolor(g,st,e,target);
        if(st.score<best){best=st.score;stale=0;}else ++stale;
        if(stale>1000 && iter%64==0) {
            int z;
            do{z=static_cast<int>(rng()%g.edge_count);}while(!allowed[z]);
            uint8_t c=static_cast<uint8_t>(rng()%5);
            if(c!=st.colors[z])apply_recolor(g,st,z,c);
        }
    }
}

static State make_seed(const Instance &g,std::mt19937_64 &rng,int type,int variant,bool preopt) {
    State st;
    if(type==0) {
        st.colors=seed_affine26(g,rng,variant);
        if(preopt) restricted_improve(g,st,allowed_star(g),rng,5000); else rebuild(g,st);
    } else if(type==1) {
        st.colors=singleton_slope_seed(g,rng);
        if(preopt) restricted_improve(g,st,allowed_vertical_star(g),rng,5000); else rebuild(g,st);
    } else {
        st.colors=balanced_random_seed(g,rng);
        rebuild(g,st);
    }
    return st;
}

static bool adversarial_delta_audit(const Instance &g,std::string &why) {
    if(!objective_audit(g,why))return false;
    std::mt19937_64 rng(6172026072302ULL);
    std::array<State,4> fixtures;
    fixtures[0].colors.assign(g.edge_count,0);
    rebuild(g,fixtures[0]);
    fixtures[1]=make_seed(g,rng,0,3,true);
    fixtures[2]=make_seed(g,rng,1,0,true);
    fixtures[3]=make_seed(g,rng,2,0,false);
    int full_replays=0;
    for(int f=0;f<4;++f) {
        if(fixtures[f].score!=score_full(g,fixtures[f].colors)){
            why="fixture initial full-score mismatch "+std::to_string(f);return false;
        }
        for(int k=0;k<40;++k) {
            int e;
            if(k<10)e=g.edge_index[k][25];
            else if(k<20)e=g.edge_index[k-10][k-10+5];
            else e=static_cast<int>(rng()%g.edge_count);
            uint8_t target;
            do{target=static_cast<uint8_t>(rng()%5);}while(target==fixtures[f].colors[e]);
            int before=fixtures[f].score;
            int predicted=delta_recolor(g,fixtures[f],e,target);
            State copy=fixtures[f];
            apply_recolor(g,copy,e,target);
            int exact=score_full(g,copy.colors);
            ++full_replays;
            if(copy.score!=exact||exact-before!=predicted){
                why="adversarial full-delta mismatch fixture "+std::to_string(f)+
                    " move "+std::to_string(k);return false;
            }
            fixtures[f]=std::move(copy);
        }
    }
    if(full_replays!=160){why="wrong full replay count";return false;}
    return true;
}

struct B2Shared {
    std::atomic<bool> stop{false};
    std::atomic<int> best{std::numeric_limits<int>::max()};
    std::atomic<uint64_t> moves{0};
    std::mutex mutex;
    fs::path out;
    std::chrono::steady_clock::time_point deadline;
    int forced_type=-1;
};

static void b2_publish(const Instance &g,B2Shared &sh,const State &st,int worker,uint64_t moves,int type) {
    int old=sh.best.load();
    while(st.score<old&&!sh.best.compare_exchange_weak(old,st.score)){}
    if(st.score<=sh.best.load()){
        std::lock_guard<std::mutex> lock(sh.mutex);
        write_raw(g,st.colors,sh.out/"best_checkpoint.col");
        std::ofstream meta(sh.out/"best_checkpoint.txt");
        meta<<"worker "<<worker<<"\nmoves "<<moves<<"\nseed_type "<<type
            <<"\nscore "<<st.score<<"\n";
    }
}

static void b2_worker(const Instance &g,B2Shared &sh,int worker,uint64_t seed) {
    std::mt19937_64 rng(seed+0x9e3779b97f4a7c15ULL*static_cast<uint64_t>(worker+1));
    uint64_t moves=0;
    int restart=0;
    auto star=allowed_star(g);
    auto vstar=allowed_vertical_star(g);
    std::vector<uint8_t> all(g.edge_count,1);
    while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline){
        int type=sh.forced_type>=0?sh.forced_type:(worker+restart)%3;
        State st=make_seed(g,rng,type,worker*101+restart*17,true);
        b2_publish(g,sh,st,worker,moves,type);
        int localbest=st.score;
        uint64_t improved=moves,start=moves;
        std::vector<uint64_t> tabu(g.edge_count,0);
        while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline&&moves-improved<40000){
            if(st.score==0){
                auto v=verify_colors(g,st.colors);
                if(!v.property_ok)throw std::runtime_error("zero score verifier disagreement");
                {std::lock_guard<std::mutex>lock(sh.mutex);
                 write_raw(g,st.colors,sh.out/"verified_hit.col");
                 std::ofstream rep(sh.out/"verified_hit_b2.txt");
                 rep<<"status VERIFIED_HIT\nworker "<<worker<<"\nmoves "<<moves
                    <<"\nseed_type "<<type<<"\nsubsets_checked "<<v.subsets_checked
                    <<"\nmissing_pairs "<<v.missing_pairs<<"\n";}
                sh.best.store(0);sh.stop.store(true);return;
            }
            const std::vector<uint8_t>* allowed=&all;
            uint64_t phase=moves-start;
            if(phase<2500&&type==0)allowed=&star;
            else if(phase<2500&&type==1)allowed=&vstar;
            uint32_t s=st.bad_sets[rng()%st.bad_sets.size()];
            uint8_t mm=st.missing_mask[s];
            int opts[5],no=0;
            for(int c=0;c<5;++c)if(mm&(1u<<c))opts[no++]=c;
            uint8_t target=static_cast<uint8_t>(opts[rng()%no]);
            int cand[15],nc=0,bestd=std::numeric_limits<int>::max();
            for(uint16_t e:g.six_edges[s]){
                if(!(*allowed)[e]||st.colors[e]==target)continue;
                int d=delta_recolor(g,st,e,target);
                if(tabu[e]>moves&&st.score+d>=sh.best.load())continue;
                if(d<bestd){bestd=d;nc=0;cand[nc++]=e;}
                else if(d==bestd)cand[nc++]=e;
            }
            if(nc==0){allowed=&all;for(uint16_t e:g.six_edges[s])if(st.colors[e]!=target){
                int d=delta_recolor(g,st,e,target);
                if(d<bestd){bestd=d;nc=0;cand[nc++]=e;}else if(d==bestd)cand[nc++]=e;}}
            if(nc==0)throw std::runtime_error("no repair move");
            int chosen;
            if(rng()%100<6){
                int eligible[15],ne=0;
                for(uint16_t e:g.six_edges[s])if((*allowed)[e]&&st.colors[e]!=target)eligible[ne++]=e;
                chosen=ne?eligible[rng()%ne]:cand[rng()%nc];
            }else chosen=cand[rng()%nc];
            apply_recolor(g,st,chosen,target);
            tabu[chosen]=moves+4+rng()%17;
            ++moves;
            if(st.score<localbest){localbest=st.score;improved=moves;b2_publish(g,sh,st,worker,moves,type);}
            if((moves&8191u)==0){
                int exact=score_full(g,st.colors);
                if(exact!=st.score)throw std::runtime_error("periodic full audit disagreement");
                sh.moves.fetch_add(8192);
            }
            if(moves-improved>8000&&moves%256==0){
                for(int k=0;k<3;++k){int e=static_cast<int>(rng()%g.edge_count);
                    uint8_t c=static_cast<uint8_t>(rng()%5);
                    if(c!=st.colors[e])apply_recolor(g,st,e,c);}
            }
        }
        ++restart;
    }
    sh.moves.fetch_add(moves&8191u);
}

static void b2_usage(){
    std::cerr<<"Usage:\n  erdos617_unrestricted_b2 --selftest\n"
             <<"  erdos617_unrestricted_b2 --seed-audit SEED\n"
             <<"  erdos617_unrestricted_b2 --search THREADS SECONDS SEED TYPE OUT_DIR\n"
             <<"TYPE is -1 portfolio, 0 affine-merged, 1 singleton+vertical, 2 balanced-random\n";
}

int main(int argc,char**argv){
    try{
        Instance g(26);
        if(argc==2&&std::string(argv[1])=="--selftest"){
            std::string why;
            if(!adversarial_delta_audit(g,why)){std::cerr<<"SELFTEST FAIL "<<why<<"\n";return 1;}
            std::cout<<"SELFTEST PASS\nbase_random_delta_audit_moves 300\n"
                     <<"adversarial_fixture_count 4\nadversarial_full_delta_replays 160\n"
                     <<"full_sixsets_per_replay 230230\n";
            return 0;
        }
        if(argc==3&&std::string(argv[1])=="--seed-audit"){
            uint64_t seed=std::stoull(argv[2]);std::mt19937_64 rng(seed);
            for(int type=0;type<3;++type){
                int best_raw=std::numeric_limits<int>::max(),best_pre=best_raw;
                for(int k=0;k<12;++k){
                    State raw=make_seed(g,rng,type,k,false);best_raw=std::min(best_raw,raw.score);
                    State pre=make_seed(g,rng,type,k,true);best_pre=std::min(best_pre,pre.score);
                    if(raw.score!=score_full(g,raw.colors)||pre.score!=score_full(g,pre.colors))
                        throw std::runtime_error("seed score replay disagreement");
                }
                std::cout<<"type "<<type<<" trials 12 best_raw "<<best_raw
                         <<" best_preoptimized "<<best_pre<<"\n";
            }
            return 0;
        }
        if(argc==7&&std::string(argv[1])=="--search"){
            int threads=std::stoi(argv[2]),seconds=std::stoi(argv[3]),type=std::stoi(argv[5]);
            uint64_t seed=std::stoull(argv[4]);fs::path out=argv[6];
            if(threads<1||threads>63||seconds<1||type< -1||type>2)throw std::runtime_error("bad args");
            std::string why;if(!adversarial_delta_audit(g,why))throw std::runtime_error("audit "+why);
            fs::create_directories(out);B2Shared sh;sh.out=out;sh.forced_type=type;
            sh.deadline=std::chrono::steady_clock::now()+std::chrono::seconds(seconds);
            std::vector<std::thread> pool;
            for(int i=0;i<threads;++i)pool.emplace_back(b2_worker,std::cref(g),std::ref(sh),i,seed);
            auto next=std::chrono::steady_clock::now()+std::chrono::seconds(5);
            while(!sh.stop.load()&&std::chrono::steady_clock::now()<sh.deadline){
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                if(std::chrono::steady_clock::now()>=next){
                    std::cout<<"best "<<sh.best.load()<<" moves "<<sh.moves.load()<<"\n";
                    next+=std::chrono::seconds(5);}
            }
            sh.stop.store(true);for(auto&t:pool)t.join();
            int best=sh.best.load();std::ofstream summary(out/"summary.txt");
            summary<<"status "<<(best==0?"VERIFIED_HIT":"NO_HIT")<<"\nthreads "<<threads
                   <<"\nseconds "<<seconds<<"\nseed "<<seed<<"\ntype "<<type
                   <<"\nbest_missing_pairs "<<best<<"\ntotal_moves "<<sh.moves.load()<<"\n";
            std::cout<<"FINAL "<<(best==0?"VERIFIED_HIT":"NO_HIT")<<" best "<<best
                     <<" moves "<<sh.moves.load()<<"\n";return best==0?0:3;
        }
        b2_usage();return 2;
    }catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<"\n";return 2;}
}
