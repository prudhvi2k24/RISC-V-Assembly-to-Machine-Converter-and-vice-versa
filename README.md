# RISC-V Assembly to Machine Code Converter

A modern web-based tool for converting between RISC-V assembly instructions and machine code. This tool supports the RV32I and RV32M instruction sets, making it perfect for students, developers, and enthusiasts working with RISC-V architecture.

## Features

- **Bidirectional Conversion**
  - Convert RISC-V assembly instructions to machine code
  - Convert machine code back to assembly instructions

- **Supported Instruction Sets**
  - RV32I Base Integer Instructions
  - RV32M Multiply/Divide Instructions

- **Instruction Types Support**
  - R-type (Register-Register)
  - I-type (Immediate)
  - S-type (Store)
  - SB-type (Branch)
  - U-type (Upper Immediate)
  - UJ-type (Jump)

- **Modern User Interface**
  - Dark theme for reduced eye strain
  - Responsive design for all devices
  - Real-time conversion
  - Interactive instruction reference
  - Example instructions for quick reference

## Usage

1. **Assembly to Machine Code**
   - Select "Assembly to Machine Code" from the dropdown
   - Enter your RISC-V assembly instruction (e.g., `add x1, x2, x3`)
   - Click "Convert" to see the machine code output

2. **Machine Code to Assembly**
   - Select "Machine Code to Assembly" from the dropdown
   - Enter your machine code
   - Click "Convert" to see the assembly instruction

## Example Instructions

- R-type: `add x1, x2, x3`
- I-type: `addi x1, x2, 10`
- S-type: `sw x1, 8(x2)`
- SB-type: `beq x1, x2, label`
- U-type: `lui x1, 0x12345`
- UJ-type: `jal x1, label`

## Supported Instructions

### RV32I Base Integer Instructions
- Arithmetic: ADD, ADDI, SUB
- Load/Store: LW, SW
- Branch: BEQ, BNE, BLT
- Jump: JAL, JALR
- System: ECALL, EBREAK

### RV32M Multiply/Divide Instructions
- Multiply: MUL, MULH
- Divide: DIV, REM

## Technical Details

The converter implements the RISC-V specification for:
- 32-bit instruction encoding
- Register-based operations
- Immediate value handling
- Branch and jump offset calculations

## Getting Started

1. Clone the repository
2. Open `index.html` in your web browser
3. Start converting instructions!

## Reference

For detailed RISC-V instruction specifications, refer to the [RISC-V Reference Card](https://dejazzer.com/coen2710/lectures/RISC-V-Reference-Data-Green-Card.pdf).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
