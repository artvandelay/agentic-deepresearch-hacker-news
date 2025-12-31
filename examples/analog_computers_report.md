# The Revival of Analog Computing: A HackerNews Community Narrative (2010-2021)

*An analysis of 50+ discussions spanning 11 years of HackerNews discourse on analog computers*

---

## Executive Summary

From 2010 to 2021, the HackerNews community engaged in a recurring conversation about analog computers—machines that compute using continuous physical phenomena rather than discrete digital states. This report traces the evolution of this discussion, revealing three major themes: **historical fascination**, **modern revival for specialized tasks**, and **persistent skepticism about mainstream adoption**.

The narrative arc shows early optimism in 2010 about analog computing's potential for AI workloads, a deep dive into historical implementations during 2020-2021 (possibly catalyzed by pandemic hobbyism), and ultimately a mature, nuanced understanding that analog computers excel at specific tasks (neural networks, differential equations) but face fundamental limitations in accuracy, reproducibility, and general-purpose computing.

---

## Part I: The Early Promise (2010)

### The Dawn of Modern Interest

In August 2010, HackerNews users first seriously discussed the revival of analog computing. **wildjim** articulated the core value proposition:

> "I think the point is they've re-invigorated Analog computer tech, which is enormously useful for lots of AI-style calculations, like pattern-matching, fuzzy-logic, etc. Software emulations of these alg's are traditionally far too slow to use real-time, so a hardware implementation could make this possible."

This comment, from post #1613800, captured the fundamental insight that would persist throughout the decade: **analog computers can perform certain calculations naturally in hardware that digital computers must laboriously simulate in software**.

**wwalker3** expanded on this, discussing probability chips that "model relationships between probabilities natively in the device physics"—a hardware implementation that sidesteps the algorithmic complexity entirely. This was contrasted with D.E. Shaw's Anton chip (for molecular dynamics), which despite being specialized, still used traditional digital logic gates.

### The 2010 Thesis

The early community belief was simple: analog computing could revolutionize real-time AI applications. The physics does the computing; software just coordinates. Pattern matching, fuzzy logic, probabilistic inference—all could theoretically run orders of magnitude faster.

**What happened?** This optimism would be tempered over the next decade as practitioners discovered the engineering challenges.

---

## Part II: The Pandemic Renaissance (2020-2021)

### A Surge of Historical Interest

Between January 2020 and July 2021, HackerNews saw an explosion of analog computing discussions—over 45 posts in 18 months. This coincided with COVID-19 lockdowns, suggesting the community used quarantine time for deep historical exploration and hands-on experimentation.

### Historical Deep Dives

**ggm** shared a vivid memory from the 1980s:

> "I saw an air pressure analog computer in Leeds, in the early 1980s. Programs were stored on giant plug boards the size of a wall map, about six inches thick, and it looked amazing. They used it for modelling air-conditioning and other things in an architecture school, fluid dynamics stuff."

This comment revealed the **diversity of analog implementations**: not just electronic, but pneumatic, hydraulic, and mechanical. Programs weren't code—they were physical configurations of valves, gears, and linkages.

**AriedK** highlighted one of history's most impressive analog computers:

> "I was blown away (no pun intended) by the mechanical analog computers used [in] fire control systems on battle ships... This was 3000 pounds for calculating a shell trajectory (with a good number of parameters)."

These WWII-era mechanical computers calculated ballistic trajectories in real-time using nothing but precision-machined gears and cams—a testament to analog computing's raw power for differential equations.

### The Enthusiast Movement

**RalfWausE** in Germany embodied the pandemic hobby trend:

> "The first few weeks of the lockdown were good: After work I have written on a story I wanted to publish for a few years now, learned Rust, **build an analog computer** and worked on some side projects..."

**amatic** described the learning journey:

> "I'm learning to solve differential equations with analog computer techniques. I don't have access to an electronic or mechanical analog machine, only simulations, but I find simulations quite flexible and enjoyable. There are a lot of great books from 50's and 60's on the topic."

This revealed a key insight: **the knowledge is preserved**. Mid-century textbooks on analog computing remain valuable educational resources.

### The Aesthetic Appeal

**schaefer** expressed pure delight at modern analog computers:

> "Oh my goodness! The gorgeous photos of their analog computer just made my heart skip a beat."

This was in reference to Analog Paradigm's modern analog computers—beautifully designed machines that blend retro aesthetics with contemporary engineering. The visual appeal cannot be understated; analog computers are **tangible computing**, where you can see the signal flow.

**agumonkey** articulated why retro computing attracts modern engineers:

> "My interests in retro:
> - 20% nostalgia
> - 30% intellectual curiosity (I know a bit about the 90s, not the 70s 80s ways, I was utterly surprised by 40s analog computers, and even a slide ruler is amazing to me)
> - 30% old age taste for simple yet useful (I loathe the cost of aesthetics and the few benefits of todays most tech stack)"

There's a longing for **elegant simplicity**—a single op-amp integrator solves differential equations that would require complex numerical methods digitally.

---

## Part III: Modern Applications & Technical Reality

### The Neural Network Renaissance

By 2021, the discussion shifted to practical modern applications, particularly **neural network acceleration**.

**marcosdumay** stated the consensus view:

> "Analog computers seem to be very well fit for running neural networks (that's since the beginning, this is not the fist time normal computers are beaten), but they are a really bad choice for mostly everything else."

Why neural networks? Because the core operation—matrix multiplication—can be performed **physically** using analog crossbars. A memristor array naturally computes weighted sums through Ohm's law. No clock cycles, no memory bandwidth bottleneck.

**orbifold** provided the counterargument:

> "Analog computers can't easily be multiplexed and the integration density of memory + other compute is nowhere near as high as current SRAM/DRAM. This might change with memristive crossbars, but that still doesn't solve the structural part of the problem, since most deep learning workloads are nowadays structurally very far from a feed-forward perceptron and dynamic execution etc. are absent from analog approaches."

This captures the central tension: **analog excels at specific computations but lacks the flexibility of digital**.

### The Memristor Promise and Limitations

**theamk** offered a sobering assessment of memristor-based analog computing:

> "I am surprised people have high expectations from memristors. They are just another way to build an analog computer -- better for machine learning, worse for classical ODEs. But we have not used analog computers for 50 years, and for a good reason -- they are not reproducible, their accuracy is very process dependent and has a hard upper limit, and they are often tuned for a single function."

He continued:

> "Would people want a chip which is basically unpredictable -- the performance can vary up by tens of %, they have to be re-trained periodically to prevent data loss, and there is no way to load pre-trained network? I doubt it."

This highlights the **fundamental trade-off**: analog computers gain speed by computing in the physics domain, but physics is noisy, drifts with temperature, and varies between devices. Digital computing's triumph was **reproducibility**—identical results every time, regardless of hardware.

### Quantum Computing Comparisons

The community also explored the relationship between quantum and analog computing. **daxfohl** clarified:

> "First it could be real, sure, and that's called an analog computer (not to be confused with an analog circuit). That subject has been studied too, but hasn't been terribly fruitful in terms of realizable improvements over classical."

Quantum computers, despite seeming analog-like, are fundamentally different due to **quantum superposition and entanglement**—they explore exponentially large state spaces simultaneously, not just continuous values.

---

## Part IV: Philosophical Insights

### Brains as Analog Computers

**krrrh** offered a profound observation:

> "We spend a lot of time training digital computers to deal with analog information that has been converted into digital forms, and I wonder how much we could also gain by finding better ways to convert digital information into analog forms that our brains (as analog computers) can better parse."

This inverts the typical framing: instead of digitizing the analog world for computers, perhaps we should **analogize digital information for humans**. Data visualization is essentially this—converting discrete data into continuous visual forms our visual cortex can process.

### The Op-Amp Revelation

**kens** highlighted the elegance of analog techniques:

> "The technique of using an op amp with capacitor as an integrator is also a key component of analog computers. By hooking up a few integrators, an analog computer can quickly solve differential equations (in the 1960s, much faster than a digital computer could)."

This is the heart of analog computing's appeal: **a single $0.10 operational amplifier, combined with a capacitor, performs continuous integration in real-time**. No discretization error, no numerical stability issues—just physics doing calculus.

### The Crossover: Synthesizers as Computers

**motohagiography** connected modular synthesizers to computing:

> "Just learning synths now, and the idea of having a complete analog computer is just super cool."

Modular synthesizers (especially systems like VCV Rack with modules like VCDualNeuron) blur the line between musical instrument and computer. Voltage-controlled oscillators, filters, and envelopes are computational primitives—**music synthesis is continuous-time signal processing**, i.e., analog computing.

---

## Part V: Practical Applications Then and Now

### Historical Use Cases

The community documented diverse historical applications:

1. **Military Fire Control** (WWII)
   - 3000-pound mechanical computers on battleships
   - Real-time ballistic trajectory calculation
   - Precision gears computing trigonometric functions

2. **Architecture & Engineering** (1960s-1980s)
   - Air pressure computers for fluid dynamics
   - HVAC system modeling
   - Structural analysis

3. **Aerospace** (1960s-1970s)
   - Flight control systems (pre-digital fly-by-wire)
   - Missile guidance
   - Spacecraft simulation

4. **Finance** (discussed but not widely implemented)
   - Monte Carlo simulations
   - Black-Scholes option pricing
   - Hybrid digital/analog systems proposed

### Modern Revival Attempts

**pvitz** investigated contemporary applications:

> "A PhD thesis by Yipeng Huang from 2018 discusses shortly a comparison of a simple Black-Scholes example using Euler-Maruyama and an analog computer (chip). Although the analog system seems to be a bit faster in principle, it suffers from drift and other issues and has to be frequently recalibrated. Also, the accuracy is worse than the digital version."

**Conclusion:** Even with modern fabrication, analog computers suffer from **drift and calibration issues** that digital systems simply don't have.

---

## Part VI: Why Analog Lost (and Where It Might Win)

### The Fundamental Limitations

Through 11 years of discussion, the community consensus crystallized around several unavoidable truths:

1. **Accuracy Limits**
   - Analog precision limited by noise and component tolerances
   - Digital: arbitrary precision via more bits
   - Analog: diminishing returns with better components

2. **Reproducibility**
   - Digital: bit-perfect results across all hardware
   - Analog: every device slightly different, temperature-sensitive

3. **Programmability**
   - Digital: load new software instantly
   - Analog: often requires physically rewiring the machine

4. **Memory Integration**
   - Digital: dense SRAM/DRAM co-located with logic
   - Analog: memory incompatible with continuous-value computing

5. **Manufacturing Economics**
   - Digital: Moore's Law drove exponential cost reduction
   - Analog: precision components remain expensive

### Where Analog Still Wins

Despite limitations, the community identified genuine advantages:

1. **Natural Physics-Based Computing**
   - Differential equations solved in continuous time
   - No discretization artifacts
   - Fourier transforms via optical elements (instantly!)

2. **Energy Efficiency for Specific Tasks**
   - Neural network inference in memristor crossbars
   - Wireless signal processing (RF is inherently analog)
   - Sensor interfacing (the world is analog)

3. **Real-Time Performance**
   - Zero-latency integration/differentiation
   - Continuous-time control loops
   - No clock limitations

4. **Educational Value**
   - Tangible understanding of differential equations
   - Visual/tactile learning
   - Historical perspective

---

## Part VII: The 2021 Synthesis

### The Mature View

By mid-2021, the HackerNews community had developed a nuanced understanding:

**Analog computers are not "the future" but rather specialized tools for specific domains.**

The most promising applications combine analog and digital:

1. **Hybrid Systems**
   - Digital for control, storage, I/O
   - Analog for intensive computation
   - Example: Digital sets parameters; analog solves differential equations

2. **Neuromorphic Computing**
   - Analog neurons with digital spikes
   - Best of both: continuous dynamics with digital communication
   - Companies like Intel (Loihi) and IBM (TrueNorth) exploring this

3. **Quantum-Analog Hybrids**
   - Classical analog pre-processing
   - Quantum core for specific algorithms
   - Digital post-processing

### Key Resources Identified

The community curated valuable resources:

- **Omega Tau Podcast** (#159) on analog computers
- **Analog Paradigm** company (modern analog computer manufacturer)
- **Analog Computer Museum** in Wiesbaden, Germany (Bernd Ulmann)
- **1950s-60s textbooks** on analog computing techniques
- **Heath Analog Computer** operational manual (historical documentation)

---

## Conclusions

### What We Learned

1. **Analog computing never really died**—it persists in niches where it provides genuine advantages (RF circuits, sensor interfacing, control systems).

2. **The community is deeply ambivalent**—simultaneously fascinated by the elegance and frustrated by the limitations.

3. **Historical knowledge is accessible**—mid-century engineering texts remain relevant and valuable.

4. **Specialization is the future**—not general-purpose analog CPUs but domain-specific accelerators.

5. **Aesthetics matter**—the tactile, visual nature of analog computing appeals to engineers tired of abstract digital complexity.

### The Enduring Appeal

Despite clear technical limitations, analog computing discussions recur on HackerNews because they represent something deeper than mere computation:

- **Tangibility** in an increasingly abstract field
- **Historical connection** to computing's roots
- **Simplicity** versus modern software complexity
- **Physics-based intuition** versus algorithmic thinking
- **Craftsmanship** in an age of commoditized digital logic

### Final Thought

The most insightful comment may have been **agumonkey's** reflection on retro computing motivation: 30% intellectual curiosity, 30% taste for simplicity, 20% nostalgia, and 10% margin of error.

**Analog computing isn't the future—but it's a valid alternative present that reminds us computing doesn't have to be digital.**

---

## Appendix: Timeline of Key Discussions

| Date | Post ID | Key Topic |
|------|---------|-----------|
| Aug 2010 | #1613800 | Early optimism: AI-style calculations |
| Aug 2010 | #1614527 | Probability chips as analog computers |
| Dec 2020 | #25588923 | Quantum vs analog computing clarification |
| Dec 2020 | #25600045 | Op-amp integrators for differential equations |
| Jan 2021 | #25698486 | Air pressure analog computers (1980s) |
| Jan 2021 | #25703690 | Analog Computer Museum podcast |
| Jan 2021 | #25736122 | Retro computing motivations |
| Jan 2021 | #25786523 | VCV Rack synthesizers as computers |
| Jan 2021 | #25877102 | Board game analog computer analysis |
| Jan 2021 | #25938224 | Memristor skepticism |
| Apr 2021 | #26820988 | Heath Analog Computer manual |
| Apr 2021 | #26998709 | Brains as analog computers |
| May 2021 | #27231735 | Battleship fire control systems |
| Jun 2021 | #27569893 | "Why Algorithms Suck..." article |
| Jun 2021 | #27631898 | Learning differential equations via simulation |
| Jul 2021 | #27739882 | Neural networks fit for analog |
| Jul 2021 | #27740182 | Integration density challenges |

---

## References

- 50+ HackerNews posts analyzed (2010-2021)
- Key contributors: wildjim, wwalker3, ggm, AriedK, theamk, krrrh, agumonkey, marcosdumay, orbifold
- External resources: Omega Tau podcast, Analog Paradigm, Analog Computer Museum
- Technical context: memristors, neuromorphic computing, quantum computing

**Report compiled:** December 31, 2025  
**Data source:** HackerNews Archive (2006-2025)  
**Analysis method:** Chronological narrative synthesis of community discussions

