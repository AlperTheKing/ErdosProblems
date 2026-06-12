from pathlib import Path
p=Path(r'E:\Projects\ErdosProblems\open307\search_307_smooth_final.cpp')
s=p.read_text()
start=s.index('vector<Den> random_unique_even_set')
mid=s.index('void update_best', start)
new=r'''
vector<Den> random_unique_even_set(const vector<Den>& pool, int minSz, int maxSz, long double low, long double high, bool avoidSmall){
  vector<Den> evens, odds; for(auto &d: pool){ if(d.even) evens.push_back(d); else odds.push_back(d); }
  vector<Den> chosen; unordered_set<int> used;
  size_t ecap=min<size_t>(evens.size(), (size_t)8);
  Den e = evens[(size_t)(rng()%ecap)]; chosen.push_back(e); used.insert(e.p); long double sum=e.inv;
  vector<pair<long double,Den>> scored; scored.reserve(odds.size());
  for(auto &d: odds){
    long double w=d.inv;
    if(avoidSmall && (d.p==3||d.p==5||d.p==7||d.p==11)) w*=0.05L;
    long double noise=0.35L + (long double)(rng()%1000000)/500000.0L;
    scored.push_back({w*noise,d});
  }
  sort(scored.begin(), scored.end(), [](auto&a, auto&b){ return a.first > b.first; });
  for(auto &sd: scored){ auto d=sd.second; if((int)chosen.size()>=maxSz) break; if(used.count(d.p)) continue; if(sum + d.inv > high && (int)chosen.size()>=minSz) continue; chosen.push_back(d); used.insert(d.p); sum += d.inv; if(sum>low && (int)chosen.size()>=minSz && (rng()%3==0)) break; }
  if(!(sum>low && sum<high && (int)chosen.size()>=minSz)) chosen.clear(); return chosen;
}
vector<Den> random_all_odd_set(const vector<Den>& pool, int minSz, int maxSz, long double low, long double high){
  vector<pair<long double,Den>> scored;
  for(auto &d: pool) if(!d.even){ long double noise=0.35L + (long double)(rng()%1000000)/500000.0L; scored.push_back({d.inv*noise,d}); }
  sort(scored.begin(), scored.end(), [](auto&a, auto&b){ return a.first > b.first; });
  vector<Den> chosen; unordered_set<int> used; long double sum=0;
  for(auto &sd: scored){ auto d=sd.second; if((int)chosen.size()>=maxSz) break; if(used.count(d.p)) continue; if(sum+d.inv>high && (int)chosen.size()>=minSz) continue; chosen.push_back(d); used.insert(d.p); sum+=d.inv; if(sum>low && (int)chosen.size()>=minSz && chosen.size()%2==0 && (rng()%3==0)) break; }
  if(!(sum>low && sum<high && (int)chosen.size()>=minSz && chosen.size()%2==0)) chosen.clear(); return chosen;
}

'''
s=s[:start]+new+s[mid:]
p.write_text(s)
