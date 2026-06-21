import React from 'react';
import { Button } from '@/components/ui/button';

export function Hero({ onStart }: { onStart: () => void }) {
  return (
    <section className="border-b-4 border-foreground newsprint-texture">
      <div className="max-w-screen-xl mx-auto grid grid-cols-1 lg:grid-cols-12">
        <div className="lg:col-span-8 p-8 md:p-16 border-b lg:border-b-0 lg:border-r border-foreground flex flex-col justify-center">
          <h1 className="text-6xl sm:text-7xl lg:text-8xl xl:text-9xl tracking-tighter leading-[0.9] mb-8">
            DISCOVER YOUR FUTURE IN ENGINEERING.
          </h1>
          <p className="text-lg font-body leading-relaxed max-w-2xl text-justify mb-8">
            <span className="text-7xl float-left mr-3 leading-[0.8] mt-2 font-serif font-black">N</span>
            avigating the MHT CET engineering admissions is complex. We provide absolute clarity by combining CAP round cutoffs, placement records, and recruiter data into a single, un-opinionated directory. No hidden algorithms. Just raw facts to help you make the right decision.
          </p>
          <div className="mt-4">
            <button 
              onClick={onStart}
              className="bg-[#111111] text-[#F9F9F7] px-8 py-4 uppercase tracking-widest font-mono text-sm border border-transparent hover:bg-white hover:text-[#111111] hover:border-[#111111] transition-all duration-200 sharp-corners inline-block hard-shadow-hover"
            >
              Start Searching Now
            </button>
          </div>
        </div>
        <div className="lg:col-span-4 p-8 bg-neutral-100 flex flex-col justify-between">
          <div>
            <h3 className="uppercase tracking-widest font-mono text-xs mb-4 border-b border-foreground pb-2">Fact Sheet</h3>
            <ul className="space-y-4 font-mono text-sm">
              <li className="flex justify-between border-b border-muted pb-2">
                <span className="text-muted-foreground">Colleges</span>
                <span className="font-bold">350+</span>
              </li>
              <li className="flex justify-between border-b border-muted pb-2">
                <span className="text-muted-foreground">Branches</span>
                <span className="font-bold">120+</span>
              </li>
              <li className="flex justify-between border-b border-muted pb-2">
                <span className="text-muted-foreground">Placements</span>
                <span className="font-bold">Tracked</span>
              </li>
              <li className="flex justify-between border-b border-muted pb-2">
                <span className="text-muted-foreground">Source</span>
                <span className="font-bold">CAP AY 2025–26</span>
              </li>
            </ul>
          </div>
          <div className="mt-12 opacity-80 mix-blend-multiply filter grayscale">
            {/* A placeholder for an image, styled like a newspaper photo */}
            <div className="aspect-square bg-[radial-gradient(#000_1px,transparent_1px)] opacity-10 [background-size:16px_16px] w-full h-full min-h-[200px] border border-foreground flex items-center justify-center p-4 text-center text-xs uppercase font-mono tracking-widest">
              Fig 1.1: Academic Infrastructure
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
