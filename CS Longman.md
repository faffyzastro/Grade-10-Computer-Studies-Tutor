CHAPTER 1: EVOLUTION AND DEVELOPMENT OF COMPUTERS
Metadata
Strand: 1.0 Foundation

Sub-strand: 1.1 Evolution and Development of Computers

Source: Longman Computer Studies Grade 10

1.1.1 Introduction
The evolution of computers is a journey from simple manual tools to the complex, high-speed machines we use today. This development is categorized into historical eras and technical generations.

1.1.2 Early Calculating Devices (Pre-Electronic Era)
The Abacus: Used for thousands of years in various cultures for arithmetic operations. It consists of a frame with beads on rods.

Napier’s Bones (1617): Invented by John Napier to simplify multiplication and division using numbered rods.

Pascaline (1642): A mechanical calculator invented by Blaise Pascal. It used a series of wheels and gears to perform addition and subtraction.

Leibniz Calculator (1673): An improvement on the Pascaline by Gottfried Leibniz that could also perform multiplication and division.

The Analytical Engine (1830s): Designed by Charles Babbage, the "Father of Computing". It was the first design for a general-purpose mechanical computer, featuring an engine for calculation, memory, and input/output components.

1.1.3 The Five Generations of Computers
The transition between generations is marked by major technological shifts in the hardware used for processing.

First Generation (1940–1956): Vacuum Tubes
Technology: Relied on vacuum tubes for circuitry.

Characteristics: Large enough to occupy entire rooms, consumed massive amounts of electricity, and produced high heat.

Memory: Used magnetic drums for primary storage.

Programming: Coded in low-level machine language.

Examples: ENIAC and UNIVAC.

Second Generation (1956–1963): Transistors
Technology: Transistors replaced vacuum tubes.

Impact: Computers became smaller, faster, cheaper, and more energy-efficient.

Memory: Shifted toward magnetic core technology.

Programming: Introduction of symbolic (Assembly) languages and early high-level languages like FORTRAN and COBOL.

Third Generation (1964–1971): Integrated Circuits (ICs)
Technology: Thousands of transistors were integrated onto a single silicon chip.

Performance: Increased speed and reliability significantly while reducing size.

Interaction: Shifted from punched cards to keyboards and monitors.

Operating Systems: Early OS allowed multiple applications to run at once.

Fourth Generation (1971–Present): Microprocessors
Technology: Thousands of integrated circuits were built onto a single silicon chip (VLSI).

The PC Era: Enabled the creation of Personal Computers (PCs), such as the IBM PC and Apple Macintosh.

Networking: Led to the development of local area networks (LANs) and eventually the Internet.

Fifth Generation (Present and Beyond): Artificial Intelligence (AI)
Technology: Based on parallel processing and superconductors.

Goal: To develop devices capable of responding to natural language input and learning/self-organization.

Applications: Voice recognition, robotics, and expert systems.

1.1.4 Summary of Trends in Evolution
Size: Continual reduction from room-sized machines to handheld devices.

Speed: Exponential increase in the number of operations performed per second.

Cost: Significant decrease in price, making computers accessible for personal and educational use.

Reliability: Increased stability and lifespan of the hardware.

CHAPTER 2: COMPUTER ARCHITECTURE
Metadata
Strand: 1.0 Foundation

Sub-strand: 1.2 Computer Architecture

Source: Longman Computer Studies Grade 10

2.1 Overview of Computer Architecture
Computer architecture refers to the internal logical structure and organization of a computer system. It defines how the hardware components (CPU, Memory, I/O) are interconnected and how they interact to process data.

2.2 The Central Processing Unit (CPU)
The CPU is the "brain" of the computer. It consists of three primary components that work together to execute instructions.

2.2.1 Arithmetic and Logic Unit (ALU)
Function: Performs all mathematical calculations (Addition, Subtraction, etc.) and logical comparisons (AND, OR, NOT, Equal to, Greater than).

Registers: Contains temporary storage locations called accumulators to hold data being processed.

2.2.2 Control Unit (CU)
Function: Acts as the manager of the CPU. It decodes instructions and sends control signals to other parts of the computer (Memory, I/O) to tell them what to do.

Clock: Synchronizes all operations using a high-speed internal clock (measured in Gigahertz, GHz).

2.2.3 Registers (Internal Memory)
High-speed storage locations inside the CPU used for immediate data access:

Program Counter (PC): Holds the address of the next instruction.

Instruction Register (IR): Holds the current instruction being executed.

Memory Address Register (MAR): Holds the memory location of data to be fetched.

2.3 Computer Memory Hierarchy
Memory is divided into primary and secondary storage based on speed and volatility.

2.3.1 Primary Memory (Main Memory)
RAM (Random Access Memory):

Volatility: Volatile (loses data when power is off).

Purpose: Holds data and programs currently in use.

ROM (Read Only Memory):

Volatility: Non-volatile.

Purpose: Holds the BIOS/firmware required to start (boot) the computer.

Cache Memory:

Purpose: Extremely fast memory located between the CPU and RAM to store frequently accessed data.

2.4 The System Bus
The System Bus is a communication pathway that connects the CPU to memory and other devices. It consists of three specific buses:

Data Bus: Carries the actual data between components. (Bi-directional)

Address Bus: Carries the location (address) of where the data is going. (Uni-directional)

Control Bus: Carries command signals (Read/Write) from the Control Unit.

2.5 The Machine Cycle (Fetch-Execute Cycle)
Every instruction goes through four stages:

Fetch: The Control Unit gets the instruction from Main Memory.

Decode: The Control Unit translates the instruction into commands.

Execute: The ALU performs the actual work.

Store: The results are written back to memory or a register.

2.6 Input and Output (I/O) Interface
The I/O interface manages communication between the CPU and external peripherals (Keyboard, Mouse, Printer).

Interrupts: A signal sent to the CPU to stop its current task and handle a priority request.

Buffers: Small memory areas that hold data temporarily while it is being transferred between a fast device (CPU) and a slow device (Printer).