import React from 'react';
import { useSearchStore } from '@/store/useSearchStore';

const SEAT_SCOPE_LABELS: Record<string, string> = {
  HU: 'Home University (HU)',
  OHU: 'Other Home University (OHU)',
  STATE: 'State Level',
};

const REGIONS = ['Mumbai', 'Navi Mumbai', 'Pune', 'Others'];

export function FilterSidebar() {
  const {
    options,
    percentile,
    percentile_buffer,
    categories,
    branches,
    seat_scopes,
    rounds,
    regions,
    setFilter,
    getLocation,
    search,
    lat,
    lng
  } = useSearchStore();

  const [catSearch, setCatSearch] = React.useState('');
  const [branchSearch, setBranchSearch] = React.useState('');

  const toggle = (key: string, value: string, current: string[]) => {
    setFilter(key as any, current.includes(value)
      ? current.filter(i => i !== value)
      : [...current, value]
    );
  };

  const filteredCategories = options?.categories.filter(c =>
    c.toLowerCase().includes(catSearch.toLowerCase())
  ) || [];

  const filteredBranches = options?.branches.filter(b =>
    b.toLowerCase().includes(branchSearch.toLowerCase())
  ) || [];

  return (
    <aside className="w-full h-full p-6 bg-background overflow-y-auto">
      <h2 className="text-2xl font-serif font-bold uppercase mb-6 pb-2 border-b-4 border-foreground">
        Filters
      </h2>

      <div className="space-y-7">

        {/* ── Percentile ── */}
        <section>
          <h3 className="font-mono text-xs tracking-widest uppercase mb-3 text-muted-foreground border-b border-muted pb-1">Cutoff Percentile</h3>
          <div className="flex flex-col gap-3">
            <div>
              <label className="text-xs uppercase font-mono block mb-1">Target Percentile</label>
              <input
                type="number"
                value={percentile}
                onChange={e => setFilter('percentile', Number(e.target.value))}
                className="w-full border-b-2 border-foreground bg-transparent px-0 py-2 font-mono text-sm focus-visible:bg-neutral-100 focus-visible:outline-none"
              />
            </div>
            <div>
              <label className="text-xs uppercase font-mono block mb-1">Buffer (+ %)</label>
              <input
                type="number"
                value={percentile_buffer}
                onChange={e => setFilter('percentile_buffer', Number(e.target.value))}
                className="w-full border-b-2 border-foreground bg-transparent px-0 py-2 font-mono text-sm focus-visible:bg-neutral-100 focus-visible:outline-none"
              />
            </div>
          </div>
        </section>

        {/* ── CAP Rounds ── */}
        <section>
          <h3 className="font-mono text-xs tracking-widest uppercase mb-3 text-muted-foreground border-b border-muted pb-1">CAP Rounds</h3>
          <div className="flex gap-4">
            {['CAP1', 'CAP2', 'CAP3'].map(r => (
              <label key={r} className="flex items-center gap-2 text-sm cursor-pointer group">
                <input
                  type="checkbox"
                  checked={rounds.includes(r)}
                  onChange={() => toggle('rounds', r, rounds)}
                  className="accent-foreground w-4 h-4"
                />
                <span className="font-mono group-hover:text-accent transition-colors">{r}</span>
              </label>
            ))}
          </div>
        </section>

        {/* ── Seat Scope ── */}
        <section>
          <h3 className="font-mono text-xs tracking-widest uppercase mb-3 text-muted-foreground border-b border-muted pb-1">Seat Scope</h3>
          <div className="space-y-2">
            {['HU', 'OHU', 'STATE'].map(s => (
              <label key={s} className="flex items-center gap-2 text-sm cursor-pointer group">
                <input
                  type="checkbox"
                  checked={seat_scopes.includes(s)}
                  onChange={() => toggle('seat_scopes', s, seat_scopes)}
                  className="accent-foreground w-4 h-4"
                />
                <span className="font-sans group-hover:text-accent transition-colors">{SEAT_SCOPE_LABELS[s]}</span>
              </label>
            ))}
          </div>
        </section>

        {/* ── Region ── */}
        <section>
          <h3 className="font-mono text-xs tracking-widest uppercase mb-3 text-muted-foreground border-b border-muted pb-1">Region</h3>
          <div className="grid grid-cols-2 gap-2">
            {REGIONS.map(r => (
              <label key={r} className="flex items-center gap-2 text-sm cursor-pointer group">
                <input
                  type="checkbox"
                  checked={regions.includes(r)}
                  onChange={() => toggle('regions', r, regions)}
                  className="accent-foreground w-4 h-4"
                />
                <span className="font-sans group-hover:text-accent transition-colors">{r}</span>
              </label>
            ))}
          </div>
        </section>

        {/* ── Location ── */}
        <section>
          <h3 className="font-mono text-xs tracking-widest uppercase mb-3 text-muted-foreground border-b border-muted pb-1">Distance (Location)</h3>
          {lat && lng ? (
            <div className="flex items-center justify-between text-xs font-mono bg-neutral-100 p-2 border border-foreground">
              <span>📍 {lat.toFixed(3)}, {lng.toFixed(3)}</span>
              <button
                onClick={() => { setFilter('lat', null); setFilter('lng', null); }}
                className="text-accent hover:underline ml-2"
              >
                Clear
              </button>
            </div>
          ) : (
            <button
              onClick={getLocation}
              className="w-full border border-foreground bg-transparent hover:bg-foreground hover:text-background px-4 py-2 text-xs font-mono uppercase tracking-widest transition-colors hard-shadow-hover"
            >
              📍 Allow Location Access
            </button>
          )}
        </section>

        {/* ── Categories ── */}
        <section>
          <h3 className="font-mono text-xs tracking-widest uppercase mb-3 text-muted-foreground border-b border-muted pb-1">Categories</h3>
          <input
            type="text"
            placeholder="Search categories..."
            value={catSearch}
            onChange={e => setCatSearch(e.target.value)}
            className="w-full border-b border-foreground bg-transparent px-2 py-1 mb-2 font-mono text-xs focus:outline-none"
          />
          <div className="max-h-48 overflow-y-auto space-y-2 border border-muted p-2">
            {filteredCategories.map(c => (
              <label key={c} className="flex items-center gap-2 text-sm cursor-pointer group">
                <input
                  type="checkbox"
                  checked={categories.includes(c)}
                  onChange={() => toggle('categories', c, categories)}
                  className="accent-foreground w-4 h-4"
                />
                <span className="group-hover:text-accent transition-colors">{c}</span>
              </label>
            ))}
            {filteredCategories.length === 0 && (
              <span className="text-xs text-muted-foreground font-mono">No categories found.</span>
            )}
          </div>
        </section>

        {/* ── Branches ── */}
        <section>
          <h3 className="font-mono text-xs tracking-widest uppercase mb-3 text-muted-foreground border-b border-muted pb-1">Branches</h3>
          <input
            type="text"
            placeholder="Search branches..."
            value={branchSearch}
            onChange={e => setBranchSearch(e.target.value)}
            className="w-full border-b border-foreground bg-transparent px-2 py-1 mb-2 font-mono text-xs focus:outline-none"
          />
          <div className="max-h-48 overflow-y-auto space-y-2 border border-muted p-2">
            {filteredBranches.map(b => (
              <label key={b} className="flex items-center gap-2 text-sm cursor-pointer group">
                <input
                  type="checkbox"
                  checked={branches.includes(b)}
                  onChange={() => toggle('branches', b, branches)}
                  className="accent-foreground w-4 h-4"
                />
                <span className="group-hover:text-accent transition-colors leading-snug">{b}</span>
              </label>
            ))}
            {filteredBranches.length === 0 && (
              <span className="text-xs text-muted-foreground font-mono">No branches found.</span>
            )}
          </div>
        </section>

        {/* ── Apply ── */}
        <div className="pb-4">
          <button
            onClick={() => search()}
            className="w-full bg-foreground text-background px-4 py-3 uppercase tracking-widest font-mono text-sm hover:bg-white hover:text-foreground border border-foreground transition-all hard-shadow-hover"
          >
            Apply Filters
          </button>
        </div>

      </div>
    </aside>
  );
}
