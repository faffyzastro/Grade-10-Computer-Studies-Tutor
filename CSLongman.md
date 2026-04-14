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

# CHAPTER 3: DATA REPRESENTATION AND PROCESSING
## Strand: 1.2 Computer Architecture (Sub-strand: Data Representation)

### Topic 1: Concepts of Data Representation
Data representation refers to the form in which data is stored, processed, and transmitted within a computer system.

#### Analogue vs. Digital Signals
* **Analogue Signal:** A signal that has a value that varies smoothly and continuously, such as human speech or a dimmer light switch.
* **Digital Signal:** A signal represented in two distinct states: 0 or 1. Computers use millions of electronic switches to represent data in these binary states (On/Off).



[Image of analogue vs digital signal waves]


### Topic 2: Coding Schemes
Coding schemes allow humans to communicate with digital computers by converting characters into binary form.
* **ASCII (American Standard Code for Information Interchange):** The most widely used scheme; it can represent 128 to 256 characters, which is sufficient for English and Western European languages.
* **Unicode:** An advanced scheme capable of representing over 65,000 characters, covering almost all written languages and symbols.

### Topic 3: Data Collection and Preparation
Data collection is the process of bringing data from various sources to one central point for analysis.

#### Methods of Data Collection:
* **Digital Repositories:** Online sources for content analysis.
* **Interviews & Questionnaires:** Structured sets of questions.
* **Automated Sources:** Barcodes, Optical Mark Recognition (OMR), Optical Character Recognition (OCR), and Magnetic Ink Character Recognition (MICR).

#### Common Data Entry Errors:
* **Transposition Errors:** Swapping the position of characters (e.g., entering 19 as 91).
* **Range Errors:** Data falling outside reasonable limits (e.g., an age of 190).
* **Consistency Errors:** Contradictory responses (e.g., a respondent identifying as male but stating they have given birth).
* **Transcription/Copying Errors:** Misidentifying characters (e.g., entering the number 0 as the letter O).

### Topic 4: Signal Conversion
* **Analogue-to-Digital Converter (ADC):** Converts continuous wave signals (like sound from a microphone) into digital data (0s and 1s).
* **Digital-to-Analogue Converter (DAC):** Converts digital data back into analogue signals (like audio played through speakers).

### Topic 5: Data Storage Units
Data is measured in bits, which are the smallest units of data a computer can process.
* **Bit:** A single binary digit (0 or 1).
* **Nibble:** A group of 4 bits.
* **Byte:** A group of 8 bits (represents one character).
* **Capacity Equivalents:** 1,024 Bytes = 1 KB; 1,024 KB = 1 MB; 1,024 MB = 1 GB; 1,024 GB = 1 TB.

### Topic 6: Number Systems
The base of a number system indicates how many digits it uses and its place value:
* **Decimal (Base 10):** Uses digits 0–9.
* **Binary (Base 2):** Uses digits 0, 1.
* **Octal (Base 8):** Uses digits 0–7.
* **Hexadecimal (Base 16):** Uses digits 0–9 and letters A–F.

### Topic 7: Binary Arithmetic (Addition)
Binary addition follows specific rules regarding "sums" and "carries".

#### Basic Rules of Binary Addition:
1. **0 + 0 = 0** (Sum 0, Carry 0)
2. **0 + 1 = 1** (Sum 1, Carry 0)
3. **1 + 0 = 1** (Sum 1, Carry 0)
4. **1 + 1 = 10** (Sum 0, Carry 1)
5. **1 + 1 + 1 = 11** (Sum 1, Carry 1)



#### Example Calculation:
To add binary numbers, align them by place value and apply the rules from right to left, carrying the 1 to the next column as needed.

This is a fully comprehensive Markdown update for **Chapter 3: Data Representation and Processing**. I have integrated the new details from your latest uploads, including **Binary Subtraction**, **Signed Numbers**, **One's and Two's Complement**, and the **Data Processing Cycle**.

---

# CHAPTER 3: DATA REPRESENTATION AND PROCESSING
## Strand: 1.0 Foundation
## Sub-strand: 1.2 Computer Architecture (Data Representation)

### Topic 1: Concepts of Data Representation
Data representation refers to the form in which data is stored, processed, and transmitted. 
* **Analogue Signal:** A signal with a value that varies smoothly and continuously, such as human speech or a dimmer light switch.
* **Digital Signal:** A signal represented in one of two distinct states: either 0 or 1, as used in a binary system.

### Topic 2: Coding Schemes
Coding schemes enable humans to communicate with computers that only use 0s and 1s.
* **ASCII:** The most widely used scheme for representing data. Standard ASCII can represent 128 characters, while extended versions represent up to 256.
* **Unicode:** A scheme capable of representing over 65,000 characters and symbols, including almost all of the world's current written languages.

### Topic 3: Data Collection and Preparation
Data collection is the process of gathering data from various sources to a central point for processing.
* **Methods:** Digital repositories, interviews, questionnaires, and automated sources like barcodes, OMR, OCR, and MICR.
* **Common Data Entry Errors:**
    * **Transposition:** Swapping the position of characters (e.g., 19 becomes 91).
    * **Range Errors:** Data outside reasonable limits (e.g., an age of 190).
    * **Consistency Errors:** Contradictory data (e.g., Male respondent indicating they have given birth).
    * **Copying/Transcription:** Misidentifying characters (e.g., 0 becomes O).

### Topic 4: Signal Conversion
* **Analogue-to-Digital Converter (ADC):** A device that converts a smooth continuous wave signal into digital numbers (0s and 1s).
* **Digital-to-Analogue Converter (DAC):** Converts digital signals back into analogue signals, such as audio for speakers.

### Topic 5: Data Storage and Capacity
Computers use a binary number system to represent data.
* **Bit:** The smallest unit of data; a binary digit (0 or 1).
* **Nibble:** A collection of 4 bits.
* **Byte:** A group of 8 bits, providing $2^8 = 256$ distinct combinations.
* **Units of Measurement:**
    * 1024 Bytes = 1 Kilobyte (KB).
    * 1024 KB = 1 Megabyte (MB).
    * 1024 MB = 1 Gigabyte (GB).
    * 1024 GB = 1 Terabyte (TB).

### Topic 6: Number Systems
The base of a number system indicates how many digits it uses.
* **Decimal (Base 10):** 0, 1, 2, 3, 4, 5, 6, 7, 8, 9.
* **Binary (Base 2):** 0, 1.
* **Octal (Base 8):** 0, 1, 2, 3, 4, 5, 6, 7.
* **Hexadecimal (Base 16):** 0–9 and A–F.

### Topic 7: Binary Arithmetic Operations
#### Binary Addition Rules:
* **0 + 0 = 0**
* **0 + 1 = 1**
* **1 + 0 = 1**
* **1 + 1 = 0 (Carry 1)**
* **1 + 1 + 1 = 1 (Carry 1)**

#### Binary Subtraction Rules:
* **0 - 0 = 0**
* **1 - 0 = 1**
* **1 - 1 = 0**
* **0 - 1 = 1 (Borrow 1 from the next column)**
> **Note:** The borrowed 1 becomes 2 units in the current column.

### Topic 8: Signed Numbers and Complements
* **Sign-Magnitude Form:** Uses the leftmost bit as a sign bit (0 for positive, 1 for negative). The remaining bits represent the magnitude.
* **One's Complement:** Obtained by flipping all bits (0s to 1s and 1s to 0s).
* **Two's Complement:** Obtained by finding the one's complement and then adding 1.
* **Overflow:** Occurs when two numbers with the same sign are added but the result has a different sign.

### Topic 9: The Data Processing Cycle
The data processing cycle follows a specific sequence of events to transform data into information.
1. **Input:** Acquiring data and entering it into the system (e.g., barcode scanners, keyboards).
2. **Processing:** Operations performed by the CPU to produce information.
3. **Storage:** Saving data/output for future use in secondary memory (e.g., hard drives, flash disks).
4. **Output:** Presenting information in the required format (e.g., monitors, printers).

### Topic 10: Data Integrity and Files
* **Data Integrity:** Identifies the quality, accuracy, and timeliness of data. Inaccurate input leads to inaccurate results (**Garbage In, Garbage Out / GIGO**).
* **Master File:** Contains permanent or semi-permanent data.
* **Transaction File:** Contains all transactions captured over a period, used to update the master file.
* **Batch Processing:** Processing that takes place in one run without human intervention.

---

Gemini said
Based on the images provided, here is the structured Markdown for Chapter 4: Computer Software. This is formatted to integrate seamlessly with your existing CS Longman.md file and is optimized for your RAG's chunking logic.

CHAPTER 4: COMPUTER SOFTWARE
Strand: 1.0 Foundation
Sub-strand: 1.5 & 1.6 Computer Software and Operating Systems
4.1 Introduction to Software
Software refers to a set of instructions (programs) that tell the computer hardware what to do. Hardware cannot perform any task without software.

4.2 Classification of Software
Computer software is broadly classified into two main categories:

System Software

Application Software

4.3 System Software
System software consists of programs that control and manage the basic operations of a computer. It acts as an interface between the hardware and the application software.

4.3.1 Operating Systems (OS)
The Operating System is the most important type of system software. It manages the computer's memory, processes, and all of its hardware and software.

Examples: Microsoft Windows, Linux, macOS, Android, and iOS.

Functions of an OS:

Processor Management: Scheduling tasks for the CPU.

Memory Management: Allocating RAM to different running programs.

File Management: Organizing data into folders and directories.

Device Management: Managing input and output devices via drivers.

User Interface: Providing a way for the user to interact with the computer.

4.3.2 Utility Programs
Utilities are service programs designed to help analyze, configure, optimize, or maintain a computer.

Examples: Antivirus software, backup tools, disk deframentalizers, and file compression tools (like WinZip).

4.3.3 Device Drivers
A device driver is a small program that tells the operating system how to communicate with a specific hardware device (e.g., a printer driver or a graphics card driver).

4.4 Application Software
Application software consists of programs designed to perform specific tasks for the user.

4.4.1 General-Purpose (Off-the-Shelf) Software
Ready-made programs developed by software companies for a wide range of users.

Word Processors: For creating text documents (e.g., MS Word, Google Docs).

Spreadsheets: For calculations and data analysis (e.g., MS Excel).

Database Management Systems (DBMS): For storing and retrieving large amounts of data (e.g., MS Access).

Presentation Software: For creating slide shows (e.g., MS PowerPoint).

4.4.2 Specific-Purpose (Bespoke/Custom-made) Software
Software developed to meet the unique requirements of a particular individual or organization (e.g., a school management system developed specifically for a certain school).

4.5 Software Acquisition and Licensing
Proprietary Software: Software that is owned by an individual or a company. Users must buy a license to use it and cannot modify the source code (e.g., Windows).

Open-Source Software: Software whose source code is made available to the public for anyone to use, modify, and distribute (e.g., Linux, VLC Media Player).

Shareware: Software provided for free on a trial basis.

Freeware: Software that is available for use at no cost.

4.6 User Interfaces
The user interface (UI) is the part of the operating system that allows a person to communicate with the computer.

Command Line Interface (CLI): The user types text commands to perform tasks (e.g., MS-DOS). It is fast but difficult for beginners to learn.

Graphical User Interface (GUI): Uses windows, icons, menus, and pointers (WIMP) to interact with the user. It is user-friendly and easy to navigate.

CHAPTER 5: INTRODUCTION TO PROGRAMMING (PASCAL)
Strand: 3.0 Software Development
Sub-strand: 3.1 & 3.3 Programming Concepts and Language Syntax
5.1 Introduction to Pascal
Pascal is a high-level, structured programming language named after the mathematician Blaise Pascal. It is designed to teach students good programming habits by enforcing a strict logical structure.

5.2 Structure of a Pascal Program
A standard Pascal program is divided into three main parts:

Program Heading: Starts with the keyword program followed by the name of the program.

Declaration Part: Where variables, constants, and data types are defined before they are used.

Statement Part (Main Body): The actual instructions, enclosed between begin and end..

Example of a Simple Program:
Delphi
program WelcomeMessage;
begin
  writeln('Welcome to Grade 10 Computer Science');
end.
5.3 Data Types in Pascal
Pascal requires every variable to have a defined data type. Common types include:

Integer: Whole numbers (e.g., 10, -5, 100).

Real: Numbers with decimal points (e.g., 3.14, 0.5).

Char: A single character (e.g., 'A', '$').

String: A sequence of characters (e.g., 'Hello Kenya').

Boolean: Logical values, either True or False.

5.4 Variables and Constants
Variables (var): Memory locations whose values can change during program execution.

Syntax: var variable_name : data_type;

Constants (const): Values that remain fixed throughout the program.

Syntax: const PI = 3.142;

5.5 Basic Pascal Statements
Assignment Statement: Used to assign a value to a variable using the := operator.

Example: Age := 16;

Input Statements:

read(): Reads data and stays on the same line.

readln(): Reads data and moves the cursor to the next line.

Output Statements:

write(): Displays output on the screen.

writeln(): Displays output and moves to a new line.

5.6 Operators in Pascal
Arithmetic: + (Addition), - (Subtraction), * (Multiplication), / (Real Division), div (Integer Division), mod (Remainder).

Relational: = (Equal to), <> (Not equal to), < (Less than), > (Greater than), <= (Less than or equal to), >= (Greater than or equal to).

Logical: and, or, not.

5.7 Programming Best Practices
Indentation: Making code readable by offsetting blocks of code.

Comments: Using (* comment *) or { comment } to explain what the code does.

Semicolons: Used as statement separators. Every statement (except those before an else or the final end.) must end with a ;.

CHAPTER 6: PROGRAM DEVELOPMENT AND ALGORITHMS
Strand: 3.0 Software Development
Sub-strand: 3.2 Program Development
6.1 Introduction to Program Development
Developing a computer program is a systematic process. It is not just about writing code; it involves a series of steps to ensure the final software is accurate, efficient, and meets user needs.

6.2 The Program Development Life Cycle (PDLC)
The PDLC consists of several stages:

Problem Recognition: Identifying the need for a software solution.

Problem Definition: Clearly stating the requirements and constraints of the problem.

Program Design: Planning the logic of the program using algorithms.

Program Coding: Translating the design into a programming language (like Pascal or Python).

Testing and Debugging: Finding and fixing errors (bugs) in the code.

Implementation: Installing and starting to use the software.

Maintenance and Review: Updating the program to fix new issues or add features.


Shutterstock
6.3 Algorithms
An algorithm is a set of step-by-step instructions used to solve a specific problem.

Properties of a good algorithm: It must be clear, finite (have an end), and produce a result.

6.3.1 Pseudocode
Pseudocode is a way of writing an algorithm using English-like statements that resemble programming code but without the strict syntax.

Keywords: START, INPUT, COMPUTE, IF...THEN...ELSE, OUTPUT, STOP.

6.3.2 Flowcharts
A flowchart is a graphical representation of an algorithm using standard symbols.

Oval (Terminal): Start/End.

Parallelogram: Input/Output.

Rectangle: Processing (Calculations).

Diamond: Decision (Yes/No questions).

Arrows: Direction of flow.

6.4 Program Control Structures
Control structures determine the order in which instructions are executed.

Sequence: Instructions are executed one after the other in a straight line.

Selection (Decision): Choosing between different paths based on a condition (e.g., IF score > 50 THEN "Pass").

Iteration (Looping): Repeating a set of instructions multiple times until a condition is met (e.g., WHILE, FOR, REPEAT...UNTIL).

6.5 Testing and Debugging
Syntax Errors: Errors caused by breaking the rules of the language (e.g., a missing semicolon).

Logical Errors: The program runs but gives the wrong answer because the math or logic is incorrect.

Runtime Errors: Errors that occur while the program is running (e.g., trying to divide by zero).

Dry Running: Manually tracing the logic of an algorithm on paper using sample data to check for errors before coding.

CHAPTER 7: COMPUTER SETUP AND SAFETY
Strand: 1.0 Foundation
Sub-strand: 1.7 Computer Setup and Safety
7.1 Introduction
Setting up a computer correctly is essential for the longevity of the hardware and the health of the user. This involves proper cable management, environmental control, and ergonomic practices.

7.2 Connecting Computer Peripherals
Peripherals are external devices connected to the system unit. They connect via specific ports:

USB (Universal Serial Bus): The most common port for keyboards, mice, and printers.

HDMI / VGA: Used for connecting monitors and projectors.

Ethernet (RJ45): Used for wired network connections.

Audio Jacks: For speakers and microphones.

The Powering Sequence:

Connect all peripherals to the system unit.

Connect the power cables to the wall socket.

Switch on the peripheral devices (monitor, printer).

Finally, press the power button on the system unit.

7.3 Safety Precautions
Safety is divided into two categories: Protecting the equipment and protecting the user.

7.3.1 Protecting the Equipment (Hardware Safety)
Stable Power: Use a UPS (Uninterruptible Power Supply) or surge protector to prevent damage from power fluctuations.

Ventilation: Ensure the system unit has enough space for airflow to prevent overheating.

Environment: Keep the room free from dust, moisture, and strong magnetic fields.

Cable Management: Use cable ties to organize wires and prevent tripping hazards.

7.3.2 Protecting the User (Ergonomics)
Ergonomics is the science of designing the workplace to fit the user's needs to prevent injury.

Posture: Sit with your back straight and feet flat on the floor.

Eye Level: The top of the monitor should be at or slightly below eye level to prevent neck strain.

Lighting: Ensure adequate lighting to avoid eye fatigue and glare on the screen.

Breaks: Follow the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds.


7.4 Common Computer Problems and Troubleshooting
Computer fails to start: Check power cables and wall sockets.

Keyboard/Mouse not responding: Check if the USB cables are firmly plugged in.

No display on monitor: Check the VGA/HDMI cable and ensure the monitor is powered on.

Slow performance: Often caused by too many open applications or lack of disk space.

7.5 Chapter Summary & Key Terms
Booting: The process of starting or restarting a computer.

Cold Boot: Starting a computer that was completely turned off.

Warm Boot: Restarting a computer that is already on (e.g., using 'Restart').

Post-Implementation Review: Checking the system after setup to ensure everything works as intended.

CHAPTER 8: DATA COMMUNICATION AND COMPUTER NETWORKS
Strand: 2.0 Computer Networking
Sub-strand: 2.1 & 2.2 Introduction to Data Communication
8.1 Introduction to Data Communication
Data communication is the process of exchanging data between two nodes (computers or devices) via some form of transmission medium, such as a wire or a wireless signal.

8.2 Components of Data Communication
For communication to occur, five basic components must be present:

Message: The information to be communicated (text, numbers, pictures, audio, video).

Sender: The device that sends the data.

Receiver: The device that receives the data.

Transmission Medium: The physical path (cables or waves) through which the message travels.

Protocols: A set of rules that govern the data communication.

8.3 Types of Data Transmission (Directional)
Simplex: Data travels in one direction only (e.g., Radio or Television broadcasting).

Half-Duplex: Data travels in both directions, but only one direction at a time (e.g., Walkie-talkies).

Full-Duplex: Data travels in both directions simultaneously (e.g., Mobile phone conversations).

8.4 Computer Networks
A computer network is a collection of computers and devices connected together to share resources (like printers and internet) and information.

8.4.1 Classification of Networks by Size
Local Area Network (LAN): Connects devices within a small geographical area like a school, office, or home.

Metropolitan Area Network (MAN): Connects devices across a city or a large campus.

Wide Area Network (WAN): Connects devices over long distances, such as countries or continents (e.g., the Internet).

8.4.2 Classification by Architecture
Client-Server Network: A powerful central computer (Server) provides resources and services to other computers (Clients).

Peer-to-Peer (P2P) Network: Every computer has equal status and can share resources directly with others without a central server.

8.5 Transmission Media
Data travels through either bounded or unbounded media:

Bounded (Wired) Media:

Twisted Pair Cable: Common for LANs (Ethernet).

Coaxial Cable: Used for cable TV and older networks.

Fiber Optic Cable: Uses light pulses to transmit data at extremely high speeds over long distances.

Unbounded (Wireless) Media:

Radio Waves: Used for Wi-Fi and Bluetooth.

Microwaves: Used for satellite and long-distance terrestrial links.

Infrared: Used for short-range communication like TV remotes.

8.6 Network Topologies
Topology refers to the physical or logical layout of a network.

Star Topology: All devices connect to a central hub or switch.

Bus Topology: All devices share a single backbone cable.

Ring Topology: Each device is connected to two others, forming a circle.

Mesh Topology: Every device is connected to every other device (highly reliable).

CHAPTER 11: EMERGING TECHNOLOGIES IN ICT
Strand: 4.0 ICT and Society
Sub-strand: 4.3 Emerging Technologies
11.1 Introduction
Emerging technologies are technical innovations which represent progressive developments within a field for competitive advantage. They are currently developing or will be available within the next few years.

11.2 Artificial Intelligence (AI)
AI is the simulation of human intelligence processes by machines, especially computer systems.

Machine Learning: A subset of AI that allows software to become more accurate in predicting outcomes without being explicitly programmed.

Natural Language Processing (NLP): Enabling computers to understand, interpret, and generate human language.

Robotics: Programmable machines capable of carrying out a series of actions autonomously or semi-autonomously.


Shutterstock
11.3 Internet of Things (IoT)
IoT refers to the network of physical objects ("things") embedded with sensors, software, and other technologies for the purpose of connecting and exchanging data with other devices over the internet.

Examples: Smart homes (smart bulbs, thermostats), wearable fitness trackers, and industrial sensors in agriculture.

11.4 Cloud Computing & Big Data
Cloud Computing: The on-demand delivery of IT resources (servers, storage, databases) over the internet with pay-as-you-go pricing.

Big Data: Extremely large data sets that may be analyzed computationally to reveal patterns, trends, and associations, especially relating to human behavior and interactions.

11.5 Blockchain Technology
A decentralized, distributed digital ledger that records transactions across many computers so that the record cannot be altered retroactively. It is the underlying technology for cryptocurrencies.

11.6 Virtual and Augmented Reality
Virtual Reality (VR): A simulated experience that can be similar to or completely different from the real world (using headsets).

Augmented Reality (AR): An interactive experience of a real-world environment where the objects that reside in the real world are enhanced by computer-generated perceptual information (e.g., Pokémon GO or specialized medical overlays).

11.7 Impact of Emerging Technologies
Positive: Improved healthcare diagnostics, personalized learning, and increased industrial productivity.

Negative: Privacy concerns, potential job displacement due to automation, and ethical dilemmas regarding AI decision-making.