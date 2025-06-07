from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///proj2.db"
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base()

class Inst(Base):
    __tablename__ = 'Inst'
    id = Column(Integer, primary_key=True, autoincrement=True)
    instruction = Column(String)
    name = Column(String)
    fmt = Column(String)
    opcode = Column(String)
    funct3 = Column(String)
    funct7 = Column(String)

class Regstore(Base):
    __tablename__ = 'Registers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    regname = Column(String)
    binary = Column(String)

class Hexc(Base):
    __tablename__ = 'Hex'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hexval = Column(String)
    binaryval = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


if __name__ == '__main__':
    instructions = [
        ('add', 'ADD','R', '0110011', '000', '0000000'),
        ('sub', 'SUB','R', '0110011', '000', '0100000'),
        ('xor', 'XOR', 'R', '0110011', '100', '0000000'),
        ('or', 'OR', 'R', '0110011', '110', '0000000'),
        ('and', 'AND', 'R', '0110011', '111', '0000000'),
        ('sll', 'Shift left logical', 'R', '0110011', '001', '0000000'),
        ('srl', 'Shift Right Logical', 'R', '0110011', '101', '0000000'),
        ('sra', 'Shift Right Arithmetic', 'R', '0110011', '101', '0100000'),
        ('slt', 'Shift less Than', 'R', '0110011', '010', '0000000'),
        ('sltu', 'Set less Than(U)', 'R', '0110011', '011', '0000000'),
        ('addi', 'ADD Immediate', 'I', '0010011', '000', None),
        ('xori', 'XOR Immediate', 'I', '0010011', '100', None),
        ('ori', 'OR Immediate', 'I', '0010011', '110', None),
        ('andi', 'AND Immediate', 'I', '0010011', '111', None),
        ('slli', 'Shift Left Logical Imm', 'I', '0010011', '001', '0000000'),
        ('srli', 'Shift Right Logical Imm', 'I', '0010011', '101', '0000000'),
        ('srai', 'Shift Right Arith Imm', 'I', '0010011', '101', '0100000'),
        ('slti', 'Set Less Than Imm', 'I', '0010011', '010', None),
        ('sltiu', 'Set Less Than Imm (U)', 'I', '0010011', '011', None),
        ('lb', 'Load Byte', 'I', '0000011', '000', None),
        ('lh', 'Load Half', 'I', '0000011', '001', None),
        ('lw', 'Load Word', 'I', '0000011', '010', None),
        ('lbu', 'Load Byte (U)', 'I', '0000011', '100', None),
        ('lhu', 'Load Half (U)', 'I', '0000011', '101', None),
        ('sb', 'Store Byte',  'S', '0100011', '000', None),
        ('sh', 'Store Half', 'S', '0100011', '001', None),
        ('sw', 'Store Word', 'S', '0100011', '010', None),
        ('beq', 'Branch ==', 'SB', '1100011', '000', None),
        ('bne','Branch !=',  'SB', '1100011', '001', None),
        ('blt', 'Branch <', 'SB', '1100011', '100', None),
        ('bge', 'Branch ≤', 'SB', '1100011', '101', None),
        ('bltu', 'Branch < (U)', 'SB', '1100011', '110', None),
        ('bgeu', 'Branch ≥ (U)', 'SB', '1100011', '111', None),
        ('jal', 'Jump And Link', 'UJ', '1101111', None, None),
        ('jalr', 'Jump And Link Reg', 'I', '1100111', '000', None),
        ('lui', 'Load Upper Imm', 'U', '0110111', None, None),
        ('auipc','Add Upper Immediate to PC', 'U', '0010111', None, None),
        ('fence','Fence', 'I', '0001111', '000' , None),
        ('fence.i','Fence', 'I', '0001111', '001' , None),
        ('csrrw','Atomic Read-Write CSR', 'I', '1110011', '001', None),
        ('csrrs','Atomic Set CSR', 'I', '1110011', '010', None),
        ('csrrc','Atomic Clear CSR', 'I', '1110011', '011', None),
        ('csrrwi','Atomic Read-Write CSR I', 'I', '1110011', '101', None),
        ('csrrsi','Atomic Set CSR I', 'I', '1110011', '110', None),
        ('csrrci','Atomic Clear CSR I', 'I', '1110011', '111', None),
        ('ecall','Environment Call', 'I', '1110011', '000', None),
        ('ebreak','Environment Break', 'I', '1110011', '001', None)
        ]

    # Add the instructions to the session
    for instruction in instructions:
        session.add(Inst(
            instruction=instruction[0],
            name=instruction[1],
            fmt=instruction[2],
            opcode=instruction[3],
            funct3=instruction[4] if instruction[4] else None,
            funct7=instruction[5] if instruction[5] else None
        ))

    # Insert registers into the 'Register' table
    registers = [
        ('zero', '00000'),
        ('x0', '00000'),
        ('ra', '00001'),
        ('x1', '00001'),
        ('sp', '00010'),
        ('x2', '00010'),
        ('gp', '00011'),
        ('x3', '00011'),
        ('tp', '00100'),
        ('x4', '00100'),
        ('t0', '00101'),
        ('x5', '00101'),
        ('t1', '00110'),
        ('x6', '00110'),
        ('t2', '00111'),
        ('x7', '00111'),
        ('x8', '01000'),
        ('s0', '01000'),
        ('fp', '01000'),
        ('s1', '01001'),
        ('x9', '01001'),
        ('a0', '01010'),
        ('a1', '01011'),
        ('a2', '01100'),
        ('a3', '01101'),
        ('a4', '01110'),
        ('a5', '01111'),
        ('a6', '10000'),
        ('a7', '10001'),
        ('s2', '10010'),
        ('s3', '10011'),
        ('s4', '10100'),
        ('s5', '10101'),
        ('s6', '10110'),
        ('s7', '10111'),
        ('s8', '11000'),
        ('s9', '11001'),
        ('s10', '11010'),
        ('s11', '11011'),
        ('t3', '11100'),
        ('t4', '11101'),
        ('t5', '11110'),
        ('t6', '11111'),
        ('x10', '01010'),
        ('x11', '01011'),
        ('x12', '01100'),
        ('x13', '01101'),
        ('x14', '01110'),
        ('x15', '01111'),
        ('x16', '10000'),
        ('x17', '10001'),
        ('x18', '10010'),
        ('x19', '10011'),
        ('x20', '10100'),
        ('x21', '10101'),
        ('x22', '10110'),
        ('x23', '10111'),
        ('x24', '11000'),
        ('x25', '11001'),
        ('x26', '11010'),
        ('x27', '11011'),
        ('x28', '11100'),
        ('x29', '11101'),
        ('x30', '11110'),
        ('x31', '11111')
    ]

    # Add the registers to the session
    for register in registers:
        print(register[0],register[1])
        session.add(Regstore(
            regname=str(register[0]),
            binary=str(register[1])
        ))

    hex1 =[
        ('0','0000'),
        ('1','0001'),
        ('2','0010'),
        ('3','0011'),
        ('4','0100'),
        ('5','0101'),
        ('6','0110'),
        ('7','0111'),
        ('8','1000'),
        ('9','1001'),
        ('A','1010'),
        ('B','1011'),
        ('C','1100'),
        ('D','1101'),
        ('E','1110'),
        ('F','1111')
    ]

    for hex in hex1:
        session.add(Hexc(
            hexval=hex[0],
            binaryval=hex[1]
        ))
    # Commit the transaction
    session.commit()

    session.close()
