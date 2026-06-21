import React from 'react';
import { CollegeResponse } from '@/store/useSearchStore';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export function CollegeCard({ college }: { college: CollegeResponse }) {
  // Determine highest cutoff to show
  const maxCutoff = college.cutoffs.reduce((max, c) => Math.max(max, c.cutoff_percentile), 0);
  const maxRecScore = college.cutoffs.reduce((max, c) => Math.max(max, c.recommendation_score || 0), 0);
  
  return (
    <Dialog>
      <DialogTrigger>
        <div className="border border-foreground bg-background p-6 hover:bg-neutral-100 hard-shadow-hover flex flex-col justify-between group cursor-pointer h-full">
          <div>
            <div className="flex justify-between items-start mb-4 gap-4">
              <h3 className="font-serif font-bold text-2xl leading-tight group-hover:text-accent transition-colors">
                {college.college_name}
              </h3>
              <span className="font-mono text-xs uppercase tracking-widest bg-foreground text-background px-2 py-1 flex-shrink-0">
                {college.college_code}
              </span>
            </div>
            
            <p className="font-mono text-sm uppercase mb-6 pb-4 border-b border-muted">
              {college.branch_name}
            </p>

            <div className="grid grid-cols-2 gap-4 font-mono text-sm mb-6">
              <div>
                <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Max Cutoff</p>
                <p className="font-bold text-lg">{maxCutoff > 0 ? maxCutoff.toFixed(2) + '%' : 'N/A'}</p>
              </div>
              {college.distance_km !== null && (
                <div>
                  <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Distance</p>
                  <p className="font-bold text-lg">{college.distance_km.toFixed(1)} km</p>
                </div>
              )}
              {college.highest_package_lpa !== null && (
                <div>
                  <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Highest Pkg</p>
                  <p className="font-bold text-lg">{college.highest_package_lpa} LPA</p>
                </div>
              )}
              {college.placement_percentage !== null && (
                <div>
                  <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Placement</p>
                  <p className="font-bold text-lg">{college.placement_percentage}%</p>
                </div>
              )}
              {maxRecScore > 0 && (
                <div>
                  <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Rec. Score</p>
                  <p className="font-bold text-lg text-accent">{maxRecScore.toFixed(1)} / 100</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t-2 border-foreground flex justify-between items-center font-mono uppercase tracking-widest bg-foreground text-background px-4 py-3 group-hover:bg-accent transition-colors">
            <span className="text-sm font-bold">View Details</span>
            <span className="text-lg group-hover:translate-x-1 transition-transform">→</span>
          </div>
        </div>
      </DialogTrigger>
      
      <DialogContent className="max-w-6xl w-[98vw] max-h-[95vh] overflow-y-auto flex flex-col sharp-corners border-2 border-foreground bg-[#F9F9F7] p-0">
        <DialogHeader className="flex-shrink-0 px-6 pt-6 pb-4 border-b-4 border-foreground">
          <div className="pr-8">
            <DialogTitle className="font-serif text-2xl font-black uppercase tracking-tighter leading-tight">
              {college.college_name}
            </DialogTitle>
            <p className="font-mono text-xs uppercase tracking-widest mt-1 text-muted-foreground">
              Code: {college.college_code} | {college.branch_name}
            </p>
          </div>
        </DialogHeader>

        <div className="overflow-y-auto flex-1 p-6 space-y-6">
          {/* Placement Details Section */}
          <section>
            <h4 className="text-xl font-serif font-bold uppercase mb-4 border-b border-foreground pb-1">Placement & Recruiters</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-sm mb-6">
              <div className="p-4 border border-foreground bg-white">
                <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Highest</p>
                <p className="font-bold">{college.highest_package_lpa ? `${college.highest_package_lpa} LPA` : 'N/A'}</p>
              </div>
              <div className="p-4 border border-foreground bg-white">
                <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Average</p>
                <p className="font-bold">{college.average_package_lpa ? `${college.average_package_lpa} LPA` : 'N/A'}</p>
              </div>
              <div className="p-4 border border-foreground bg-white">
                <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Median</p>
                <p className="font-bold">{college.median_package_lpa ? `${college.median_package_lpa} LPA` : 'N/A'}</p>
              </div>
              <div className="p-4 border border-foreground bg-white">
                <p className="text-muted-foreground text-xs uppercase tracking-widest mb-1">Placed</p>
                <p className="font-bold">{college.placement_percentage ? `${college.placement_percentage}%` : 'N/A'}</p>
              </div>
            </div>
            
            {college.top_recruiters && (
              <div className="border border-foreground p-4 bg-white">
                <h5 className="font-mono text-xs tracking-widest uppercase mb-2 text-muted-foreground">Top Recruiters</h5>
                <p className="font-sans text-sm">{college.top_recruiters}</p>
              </div>
            )}
          </section>

          {/* Cutoffs Section */}
          <section>
            <h4 className="text-xl font-serif font-bold uppercase mb-4 border-b border-foreground pb-1">Cutoff History</h4>
            <div className="overflow-x-auto border border-foreground max-h-64 overflow-y-auto">
              <table className="w-full text-left border-collapse font-sans text-sm">
                <thead>
                  <tr className="bg-foreground text-background font-mono text-xs uppercase tracking-widest">
                    <th className="p-3 border-r border-background/20">Round</th>
                    <th className="p-3 border-r border-background/20">Category</th>
                    <th className="p-3 border-r border-background/20">Scope</th>
                    <th className="p-3 border-r border-background/20">Rank</th>
                    <th className="p-3 border-r border-background/20">Percentile</th>
                    <th className="p-3">Rec. Score</th>
                  </tr>
                </thead>
                <tbody>
                  {college.cutoffs.length > 0 ? (
                    college.cutoffs.map((cutoff, idx) => (
                      <tr key={idx} className="border-b border-muted hover:bg-neutral-100 transition-colors">
                        <td className="p-3 border-r border-muted font-bold">{cutoff.cap_round}</td>
                        <td className="p-3 border-r border-muted">{cutoff.category}</td>
                        <td className="p-3 border-r border-muted">{cutoff.seat_scope}</td>
                        <td className="p-3 border-r border-muted font-mono">{cutoff.cutoff_rank}</td>
                        <td className="p-3 border-r border-muted font-mono font-bold">{cutoff.cutoff_percentile.toFixed(2)}%</td>
                        <td className="p-3 font-mono font-bold text-accent">
                          {cutoff.recommendation_score ? cutoff.recommendation_score.toFixed(1) : '-'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="p-4 text-center font-mono text-muted-foreground">No cutoff data available</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </div> {/* end scrollable body */}
      </DialogContent>
    </Dialog>
  );
}
