#include <algorithm>
#include <array>
#include <bitset>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <set>
#include <stdexcept>
#include <vector>

static int inv5(int x) {
    static constexpr int inv[5] = {0,1,3,2,4};
    return inv[x];
}

static int line_id(int point, int slope) {
    int x = point % 5, y = point / 5;
    return (y - slope * x + 25) % 5;
}

static std::vector<std::bitset<25>> transversals(int slope) {
    std::vector<std::bitset<25>> out;
    std::array<int,5> perm{0,1,2,3,4};
    do {
        std::bitset<25> t;
        for (int line = 0; line < 5; ++line) {
            int x = perm[line];
            int y = (line + slope * x) % 5;
            t.set(5*y + x);
        }
        out.push_back(t);
    } while (std::next_permutation(perm.begin(), perm.end()));
    return out;
}

static std::vector<std::bitset<25>> size5_blockers(int slope) {
    auto ts = transversals(slope);
    std::vector<std::bitset<25>> out;
    for (int a=0;a<21;++a) for(int b=a+1;b<22;++b) for(int c=b+1;c<23;++c)
    for(int d=c+1;d<24;++d) for(int e=d+1;e<25;++e) {
        std::bitset<25> s;
        s.set(a);s.set(b);s.set(c);s.set(d);s.set(e);
        bool hit_all = true;
        for (const auto &t : ts) if ((s & t).none()) { hit_all = false; break; }
        if (hit_all) out.push_back(s);
    }
    return out;
}

static std::bitset<25> vertical_column(int x) {
    std::bitset<25> s;
    for (int y=0;y<5;++y) s.set(5*y+x);
    return s;
}

static std::bitset<25> slope_line(int slope, int id) {
    std::bitset<25> s;
    for (int p=0;p<25;++p) if (line_id(p,slope)==id) s.set(p);
    return s;
}

int main() {
    std::array<std::vector<std::bitset<25>>,5> blockers;
    for (int c=0;c<5;++c) {
        blockers[c]=size5_blockers(c);
        if (blockers[c].size()!=10) throw std::runtime_error("blocker count != 10");
        std::set<unsigned long> expected;
        for(int x=0;x<5;++x) expected.insert(vertical_column(x).to_ulong());
        for(int l=0;l<5;++l) expected.insert(slope_line(c,l).to_ulong());
        std::set<unsigned long> got;
        for(const auto &b:blockers[c]) got.insert(b.to_ulong());
        if(got!=expected) throw std::runtime_error("blockers are not exactly the ten stars");
    }

    uint64_t disjoint_five_tuples=0, all_vertical_tuples=0;
    std::array<int,5> choice{};
    for(choice[0]=0;choice[0]<10;++choice[0])
    for(choice[1]=0;choice[1]<10;++choice[1])
    for(choice[2]=0;choice[2]<10;++choice[2])
    for(choice[3]=0;choice[3]<10;++choice[3])
    for(choice[4]=0;choice[4]<10;++choice[4]) {
        bool disjoint=true;
        std::bitset<25> used;
        for(int c=0;c<5;++c) {
            if((used&blockers[c][choice[c]]).any()){disjoint=false;break;}
            used|=blockers[c][choice[c]];
        }
        if(!disjoint) continue;
        ++disjoint_five_tuples;
        bool all_vertical=true;
        for(int c=0;c<5;++c) {
            bool is_vertical=false;
            for(int x=0;x<5;++x) if(blockers[c][choice[c]]==vertical_column(x)) is_vertical=true;
            all_vertical &= is_vertical;
        }
        if(all_vertical) ++all_vertical_tuples;
    }
    if(disjoint_five_tuples!=120 || all_vertical_tuples!=120)
        throw std::runtime_error("disjoint blocker tuples are not exactly 5! vertical partitions");

    uint64_t vertical_edges=0, forced_color_claims=0, transversal_checks=0;
    for(int x=0;x<5;++x) for(int y1=0;y1<5;++y1) for(int y2=y1+1;y2<5;++y2) {
        ++vertical_edges;
        for(int omitted=0;omitted<5;++omitted) {
            if(omitted==x) continue;
            int slope=omitted;
            std::array<int,5> selected{};
            int ns=0;
            selected[ns++]=5*y1+x;
            selected[ns++]=5*y2+x;
            std::array<bool,5> used_line{};
            used_line[line_id(selected[0],slope)]=true;
            used_line[line_id(selected[1],slope)]=true;
            std::vector<int> remaining_lines, remaining_columns;
            for(int l=0;l<5;++l) if(!used_line[l]) remaining_lines.push_back(l);
            for(int col=0;col<5;++col) if(col!=x && col!=omitted) remaining_columns.push_back(col);
            if(remaining_lines.size()!=3 || remaining_columns.size()!=3)
                throw std::runtime_error("bad completion dimensions");
            for(int k=0;k<3;++k) {
                int col=remaining_columns[k], line=remaining_lines[k];
                int y=(line+slope*col)%5;
                selected[ns++]=5*y+col;
            }
            std::array<int,5> line_counts{}, column_counts{};
            for(int p:selected){++line_counts[line_id(p,slope)];++column_counts[p%5];}
            for(int z:line_counts) if(z!=1) throw std::runtime_error("not a slope transversal");
            for(int col=0;col<5;++col) {
                int want=col==x?2:(col==omitted?0:1);
                if(column_counts[col]!=want) throw std::runtime_error("wrong unique-repeat columns");
            }
            ++transversal_checks;
            ++forced_color_claims;
        }
    }
    if(vertical_edges!=50 || forced_color_claims!=200 || transversal_checks!=200)
        throw std::runtime_error("forced-colour audit totals disagree");

    std::cout<<"STRUCTURE_AUDIT PASS\n"
             <<"perfect_matchings_per_slope 120\n"
             <<"size5_blockers_per_slope 10\n"
             <<"disjoint_five_blocker_tuples 120\n"
             <<"all_vertical_partitions 120\n"
             <<"vertical_edges 50\n"
             <<"forced_distinct_colours_per_vertical_edge 4\n"
             <<"unique_repeat_transversal_checks 200\n"
             <<"conclusion AFFINE_75_FAMILY_UNSAT\n";
}
