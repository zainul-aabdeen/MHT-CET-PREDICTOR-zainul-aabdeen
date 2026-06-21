import React from 'react';

export function Navbar() {
  return (
    <header className="sticky top-0 z-40 bg-background border-b-4 border-foreground px-4 py-3">
      <div className="max-w-screen-xl mx-auto flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold uppercase tracking-widest font-sans">The College Times</h1>
          <p className="text-xs font-mono uppercase text-muted-foreground mt-1">Vol. 1 | AY 2025–2026 | Maharashtra Edition</p>
        </div>
        <div className="font-mono text-xs uppercase tracking-widest text-muted-foreground">
          MHT CET CAP Round Directory
        </div>
      </div>
    </header>
  );
}
