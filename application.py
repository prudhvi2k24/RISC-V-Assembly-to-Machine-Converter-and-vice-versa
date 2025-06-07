from Init import Regstore, Inst, Hexc
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String
import re
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

DATABASE_URL = "sqlite:///proj2.db"
engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)
session = Session()

def binary_to_hex(binary):
    hexval =''
    binary = binary.replace('_','')
    for i in binary:
        if i != '0' and i != '1':
            return 'Invalid Binary'
    while(len(binary) >= 4):
        temp = binary[-4:]
        hex = session.query(Hexc).filter(Hexc.binaryval == temp).first()
        hexval = hex.hexval + hexval
        binary = binary[:-4]
    if len(binary) > 0:
        while len(binary) < 4:
            binary = '0' + binary
        hex = session.query(Hexc).filter(Hexc.binaryval == binary).first()
        hexval = hex.hexval + hexval

    return '0x' + hexval

def hex_to_binary(hexval):
    hexval = hexval.replace('0x','').strip()
    binary = ''
    while len(hexval) > 0:
        hex = session.query(Hexc).filter(Hexc.hexval == hexval[-1].upper()).first()
        binary = hex.binaryval + binary
        hexval = hexval[:-1]
    return binary

def imm_to_binary(imm,fill=12):
    if '0x' in imm.lower():
        return hex_to_binary(imm).zfill(fill)
    else:
        number = int(imm)
        #print('Decimal')
        if number < 0:
            return(bin((1<<fill) + number)[2:].zfill(fill))
        else:
            return(bin(number)[2:].zfill(fill))

def calc_decimal(binary):
    decimal = 0
    power = 0
    for digit in reversed(binary):
        if digit == '1':
            decimal += 2**power
        power += 1
    return str(decimal)

def assembly_to_machine_Rtype(opcode, funct3, funct7, rd, rs1, rs2):
    rdi=session.query(Regstore).filter(Regstore.regname == rd).first()
    print(rdi.binary,end='\n')
    rs1i=session.query(Regstore).filter(Regstore.regname == rs1).first()
    print(rs1i.binary,end='\n')
    rs2i=session.query(Regstore).filter(Regstore.regname == rs2).first()
    print(rs2i.binary,end='\n')
    if rdi is None or rs1i is None or rs2i is None:
        return 'Invalid Register'
    return binary_to_hex(funct7 + rs2i.binary + rs1i.binary + funct3 + rdi.binary + opcode)

def assembly_to_machine_Itype(opcode, funct3, rd, rs1, imm):
    print(opcode,funct3,rd,rs1,imm)
    if opcode == '1100111' or opcode =='0000011':
        rs1, imm = imm, rs1
    rdi=session.query(Regstore).filter(Regstore.regname == rd).first()
    print(rdi.binary)
    rs1i=session.query(Regstore).filter(Regstore.regname == rs1).first()
    print(rs1i.binary)
    if rdi is None or rs1i is None:
        return 'Invalid Register'
    return binary_to_hex(imm_to_binary(imm) + rs1i.binary + funct3 + rdi.binary + opcode)

def assembly_to_machine_Stype(opcode, funct3, rs2, imm, rs1):
    rs1i=session.query(Regstore).filter(Regstore.regname == rs1).first()
    rs2i=session.query(Regstore).filter(Regstore.regname == rs2).first()
    if rs1i is None or rs2i is None:
        return 'Invalid Register'
    imm = imm_to_binary(imm,12)
    print(imm[0:7],rs2i.binary,rs1i.binary,funct3,imm[7:],opcode,end='\n')
    return binary_to_hex(imm[0:7] + rs2i.binary + rs1i.binary + funct3 + imm[7:] + opcode)

def assembly_to_machine_Utype(opcode, rd, imm):
    rdi=session.query(Regstore).filter(Regstore.regname == rd).first()
    if rdi is None:
        return 'Invalid Register'
    return binary_to_hex(imm_to_binary(imm,20) + rdi.binary + opcode)

def assembly_to_machine_SBtype(opcode, funct3, rs1, rs2, imm):
    rs1i=session.query(Regstore).filter(Regstore.regname == rs1).first()
    rs2i=session.query(Regstore).filter(Regstore.regname == rs2).first()
    if rs1i is None or rs2i is None:
        return 'Invalid Register'
    imm = imm_to_binary(imm,13)
    #print(imm,end="\n\n")
    return binary_to_hex(imm[-13] + imm[-11:-5] + rs2i.binary + rs1i.binary + funct3 + imm[-5:-1] + imm[-12] + opcode)

def assembly_to_machine_UJtype(opcode,rd,imm):
    rdi=session.query(Regstore).filter(Regstore.regname == rd).first()
    if rdi is None:
        return 'Invalid Register'
    imm=imm_to_binary(imm,21)
    return binary_to_hex(imm[-21]+imm[-11:-1]+imm[-12]+imm[-20:-12] + rdi.binary + opcode)

def assembly_to_machine_Fence(opcode, funct3, pred, succ):
    # For fence instructions, pred and succ are 4-bit fields
    # Convert pred and succ to binary, ensuring they are 4 bits
    pred = pred.lower()
    succ = succ.lower()
    pred_bin = ['0']*4
    succ_bin = ['0']*4
    if 'i' in pred:
        pred_bin[0] = '1'
    if 'o' in pred:
        pred_bin[1] = '1'
    if 'r' in pred:
        pred_bin[2] = '1'
    if 'w' in pred:
        pred_bin[3] = '1'
    if 'i' in succ:
        succ_bin[0] = '1'
    if 'o' in succ:
        succ_bin[1] = '1'
    if 'r' in succ:
        succ_bin[2] = '1'
    if 'w' in succ:
        succ_bin[3] = '1'
    # The immediate field is pred + succ + 4 zeros + 4 zeros
    imm = ''.join(pred_bin) + ''.join(succ_bin) + '0000'
    # For fence.i, we don't need pred and succ, so we use zeros
    if funct3 == '001':  # fence.i
        imm = '0' * 12
    print(imm)
    return binary_to_hex(imm + '00000' + funct3 + '00000' + opcode)

def assembly_to_machine_CSR(opcode, funct3, rd, csr, rs1):
    # For CSR instructions, csr is a 12-bit immediate value
    # Convert csr to binary, ensuring it's 12 bits
    if '0x' in csr.lower():
        csr_bin = bin(int(csr, 16))[2:].zfill(12)
    else:
        csr_bin = bin(int(csr))[2:].zfill(12)
    #print(csr_bin,rd,rs1)
    # Get register binary values
    rdi = session.query(Regstore).filter(Regstore.regname == rd).first()
    rs1i = session.query(Regstore).filter(Regstore.regname == rs1).first()

    if rdi is None or rs1i is None:
        return 'Invalid Register'

    return binary_to_hex(csr_bin + rs1i.binary + funct3 + rdi.binary + opcode)

def assembly_to_machine_CSRI(opcode, funct3, rd, csr, imm):
    # For CSR immediate instructions, imm is a 5-bit immediate value
    # Convert imm to binary, ensuring it's 5 bits
    if '0x' in imm.lower():
        imm_bin = bin(int(imm, 16))[2:].zfill(5)
    else:
        imm_bin = bin(int(imm))[2:].zfill(5)

    # Get register binary value
    rdi = session.query(Regstore).filter(Regstore.regname == rd).first()

    if rdi is None:
        return 'Invalid Register'

    # Convert csr to binary
    if '0x' in csr.lower():
        csr_bin = bin(int(csr, 16))[2:].zfill(12)
    else:
        csr_bin = bin(int(csr))[2:].zfill(12)

    return binary_to_hex(csr_bin + imm_bin + funct3 + rdi.binary + opcode)

def assembly_to_machine_Sys(opcode, funct3):
    # For system instructions (ecall, ebreak), all fields are zero except opcode and funct3
    return binary_to_hex('0' * 20 + funct3 + '00000' + opcode)

def machine_to_assembly_Rtype(opcode, funct3, funct7, rs1, rs2, rd):
    rdi=session.query(Regstore).filter(Regstore.binary == rd).first()
    rs1i=session.query(Regstore).filter(Regstore.binary == rs1).first()
    rs2i=session.query(Regstore).filter(Regstore.binary == rs2).first()
    if rdi is None or rs1i is None or rs2i is None:
        return 'Invalid Register'
    instance = session.query(Inst).filter(Inst.opcode == opcode, Inst.funct3 == funct3, Inst.funct7 == funct7).first()
    if instance is None:
        return 'Invalid Instruction'
    return instance.instruction + ' ' + rdi.regname + ', ' + rs1i.regname + ', ' + rs2i.regname

def machine_to_assembly_Itype(opcode, funct3, rs1, imm, rd):
    rdi=session.query(Regstore).filter(Regstore.binary == rd).first()
    rs1i=session.query(Regstore).filter(Regstore.binary == rs1).first()
    if rdi is None or rs1i is None:
        return 'Invalid Register'
    instance = session.query(Inst).filter(Inst.opcode == opcode, Inst.funct3 == funct3).first()
    if instance is None:
        return 'Invalid Instruction'

    # Convert immediate to decimal
    imm_decimal = int(imm, 2)
    if imm[0] == '1':  # If negative (sign bit is 1)
        imm_decimal = imm_decimal - (1 << len(imm))  # Convert to negative using two's complement

    if opcode == '1100111' or opcode == '0000011':
        return instance.instruction + ' ' + rdi.regname + ', ' + str(imm_decimal) + '(' + rs1i.regname + ')'
    else:
        return instance.instruction + ' ' + rdi.regname + ', ' + rs1i.regname + ', ' + str(imm_decimal)

def machine_to_assembly_Stype(opcode, funct3, rs2, imm, rs1):
    rs1i=session.query(Regstore).filter(Regstore.binary == rs1).first()
    rs2i=session.query(Regstore).filter(Regstore.binary == rs2).first()
    if rs1i is None or rs2i is None:
        return 'Invalid Register'
    instance = session.query(Inst).filter(Inst.opcode == opcode, Inst.funct3 == funct3).first()
    if instance is None:
        return 'Invalid Instruction'
    return instance.instruction + ' ' + rs2i.regname + ', ' + binary_to_hex(imm) + '(' + rs1i.regname + ')'

def machine_to_assembly_Utype(opcode,rd,imm):
    rdi=session.query(Regstore).filter(Regstore.binary == rd).first()
    if rdi is None:
        return 'Invalid Register'
    instance = session.query(Inst).filter(Inst.opcode == opcode).first()
    if instance is None:
        return 'Invalid Instruction'
    return instance.instruction + ' ' + rdi.regname + ', ' + binary_to_hex(imm)

def machine_to_assembly_SBtype(opcode, funct3, rs1, rs2, imm):
    rs1i=session.query(Regstore).filter(Regstore.binary == rs1).first()
    rs2i=session.query(Regstore).filter(Regstore.binary == rs2).first()
    if rs1i is None or rs2i is None:
        return 'Invalid Register'
    instance = session.query(Inst).filter(Inst.opcode == opcode, Inst.funct3 == funct3).first()
    if instance is None:
        return 'Invalid Instruction'
    return instance.instruction + ' ' + rs1i.regname + ', ' + rs2i.regname + ', ' + calc_decimal(imm)

def machine_to_assembly_UJtype(opcode, rd, imm):
    rdi=session.query(Regstore).filter(Regstore.binary == rd).first()
    if rdi is None:
        return 'Invalid Register'
    instance = session.query(Inst).filter(Inst.opcode == opcode).first()
    if instance is None:
        return 'Invalid Instruction'
    return instance.instruction + ' ' + rdi.regname + ', ' + binary_to_hex(imm)

def machine_to_assembly_Fence(opcode, funct3, imm):
    instance = session.query(Inst).filter(Inst.opcode == opcode, Inst.funct3 == funct3).first()
    if instance is None:
        return 'Invalid Instruction'
    if funct3 == '001':  # fence.i
        return instance.instruction
    else:  # fence
        pred_bin = imm[:4]
        succ_bin = imm[4:8]
        pred = ''
        succ = ''
        if pred_bin[0] == '1':
            pred += 'I'
        if pred_bin[1] == '1':
            pred += 'O'
        if pred_bin[2] == '1':
            pred += 'R'
        if pred_bin[3] == '1':
            pred += 'W'
        if succ_bin[0] == '1':
            succ += 'I'
        if succ_bin[1] == '1':
            succ += 'O'
        if succ_bin[2] == '1':
            succ += 'R'
        if succ_bin[3] == '1':
            succ += 'W'
        pred = pred.upper()
        succ = succ.upper()
        return instance.instruction.upper() + ' ' + pred + ', ' + succ

def machine_to_assembly_CSR(opcode, funct3, csr, rs1, rd):

    rdi = session.query(Regstore).filter(Regstore.binary == rd).first()
    rs1i = session.query(Regstore).filter(Regstore.binary == rs1).first()

    if rdi is None or rs1i is None:
        return 'Invalid Register'

    instance = session.query(Inst).filter(Inst.opcode == opcode, Inst.funct3 == funct3).first()
    if instance is None:
        return 'Invalid Instruction'

    return instance.instruction + ' ' + rdi.regname + ', ' + hex(int(csr, 2)) + ', ' + rs1i.regname

def machine_to_assembly_CSRI(opcode, funct3, csr, imm, rd):
    rdi = session.query(Regstore).filter(Regstore.binary == rd).first()

    print(rd,csr,imm)

    if rdi is None:
        return 'Invalid Register'

    instance = session.query(Inst).filter(Inst.opcode == opcode, Inst.funct3 == funct3).first()
    if instance is None:
        return 'Invalid Instruction'

    return instance.instruction + ' ' + rdi.regname + ', ' + hex(int(csr, 2)) + ', ' + str(int(imm, 2))

def machine_to_assembly_Sys(opcode, funct3):
    instance = session.query(Inst).filter(Inst.opcode == opcode, Inst.funct3 == funct3).first()
    if instance is None:
        return 'Invalid Instruction'
    return instance.instruction

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'result': 'Invalid request: No JSON data provided'})

        choice = data.get('choice')
        instruction = data.get('instruction').strip().lower()

        if not choice or not instruction:
            return jsonify({'result': 'Invalid request: Missing choice or instruction'})

        if choice == 1:
            instruction = re.split(r'[ ,()]+', instruction)

            inst = session.query(Inst).filter(Inst.instruction == instruction[0].lower()).first()

            if inst is None:
                return jsonify({'result': 'Invalid instruction'})

            result = []
            if inst.fmt == 'R':
                result.append("Given instruction is of R type.\n")
                result.append("R-type format: | funct7 | rs2 | rs1 | funct3 | rd | opcode |\n")
                result.append("              | 7 bits | 5 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                result.append("\nField Values:\n")
                result.append(f"Opcode: {inst.opcode}")
                result.append(f"Funct3: {inst.funct3}")
                result.append(f"Funct7: {inst.funct7}")
                try:
                    rd_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                    rs1_bin = session.query(Regstore).filter(Regstore.regname == instruction[2]).first().binary
                    rs2_bin = session.query(Regstore).filter(Regstore.regname == instruction[3]).first().binary
                    result.append(f"Rd: {instruction[1]} (binary: {rd_bin})")
                    result.append(f"Rs1: {instruction[2]} (binary: {rs1_bin})")
                    result.append(f"Rs2: {instruction[3]} (binary: {rs2_bin})")
                    result.append(f"\nMachine code for provided assembly code: {assembly_to_machine_Rtype(inst.opcode, inst.funct3, inst.funct7, instruction[1], instruction[2], instruction[3])}")
                except Exception as e:
                    return jsonify({'result': f'Error processing registers: {str(e)}'})
            elif inst.fmt == 'I':
                if inst.instruction == 'fence' or inst.instruction == 'fence.i':
                    result.append("Given instruction is a fence instruction.\n")
                    result.append("Fence format: | imm[11:0] | rs1 | funct3 | rd | opcode |\n")
                    result.append("              | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {inst.opcode}")
                    result.append(f"Funct3: {inst.funct3}")
                    if inst.instruction == 'fence':
                        result.append(f"Machine code for provided assembly code: {assembly_to_machine_Fence(inst.opcode, inst.funct3, instruction[1], instruction[2])}")
                    else:
                        result.append(f"Machine code for provided assembly code: {assembly_to_machine_Fence(inst.opcode, inst.funct3, '0', '0')}")
                elif inst.instruction in ['csrrw', 'csrrs', 'csrrc']:
                    result.append("Given instruction is a CSR instruction.\n")
                    result.append("CSR format: | csr | rs1 | funct3 | rd | opcode |\n")
                    result.append("            | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {inst.opcode}")
                    result.append(f"Funct3: {inst.funct3}")
                    rd_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                    rs1_bin = session.query(Regstore).filter(Regstore.regname == instruction[3]).first().binary
                    result.append(f"Rd: {instruction[1]} (binary: {rd_bin})")
                    result.append(f"Rs1: {instruction[3]} (binary: {rs1_bin})")
                    result.append(f"CSR: {instruction[2]}")
                    result.append(f"Machine code for provided assembly code: {assembly_to_machine_CSR(inst.opcode, inst.funct3, instruction[1], instruction[2], instruction[3])}")
                elif inst.instruction in ['csrrwi', 'csrrsi', 'csrrci']:
                    result.append("Given instruction is a CSR immediate instruction.\n")
                    result.append("CSR-I format: | csr | zimm | funct3 | rd | opcode |\n")
                    result.append("              | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {inst.opcode}")
                    result.append(f"Funct3: {inst.funct3}")
                    rd_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                    result.append(f"Rd: {instruction[1]} (binary: {rd_bin})")
                    result.append(f"Zimm: {instruction[3]}")
                    result.append(f"CSR: {instruction[2]}")
                    result.append(f"Machine code for provided assembly code: {assembly_to_machine_CSRI(inst.opcode, inst.funct3, instruction[1], instruction[2], instruction[3])}")
                elif inst.instruction in ['ecall', 'ebreak']:
                    result.append("Given instruction is a system instruction.\n")
                    result.append("System format: | funct12 | rs1 | funct3 | rd | opcode |\n")
                    result.append("               | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {inst.opcode}")
                    result.append(f"Funct3: {inst.funct3}")
                    result.append(f"Machine code for provided assembly code: {assembly_to_machine_Sys(inst.opcode, inst.funct3)}")
                else:
                    result.append("Given instruction is of I type.\n")
                    result.append("I-type format: | imm[11:0] | rs1 | funct3 | rd | opcode |\n")
                    result.append("               | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {inst.opcode}")
                    result.append(f"Funct3: {inst.funct3}")
                    print("instruction: {} , Rd: {} , Rs1: {} , Imm: {}".format(inst.instruction, instruction[1], instruction[2], instruction[3]))
                    if(inst.instruction == 'lw' or inst.instruction == 'lh' or inst.instruction == 'lb' or inst.instruction == 'lhu' or inst.instruction == 'lbu'):
                        rd_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                        rs1_bin = session.query(Regstore).filter(Regstore.regname == instruction[3]).first().binary
                        imm_bin = imm_to_binary(instruction[2])
                        result.append(f"Rd: {instruction[1]} (binary: {rd_bin})")
                        result.append(f"Rs1: {instruction[3]} (binary: {rs1_bin})")
                        result.append(f"Imm: {instruction[2]}")
                    else:
                        rd_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                        rs1_bin = session.query(Regstore).filter(Regstore.regname == instruction[2]).first().binary
                        imm_bin = imm_to_binary(instruction[3])
                        result.append(f"Rd: {instruction[1]} (binary: {rd_bin})")
                        result.append(f"Rs1: {instruction[2]} (binary: {rs1_bin})")
                        result.append(f"Imm: {instruction[3]}")
                    result.append(f"\nMachine code for provided assembly code: {assembly_to_machine_Itype(inst.opcode, inst.funct3, instruction[1], instruction[2], instruction[3])}")
            elif inst.fmt == 'S':
                result.append("Given instruction is of S type.\n")
                result.append("S-type format: | imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode |\n")
                result.append("               | 7 bits | 5 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                result.append("\nField Values:\n")
                result.append(f"Opcode: {inst.opcode}")
                result.append(f"Funct3: {inst.funct3}")
                rs1_bin = session.query(Regstore).filter(Regstore.regname == instruction[3]).first().binary
                rs2_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                result.append(f"Rs1: {instruction[3]} (binary: {rs1_bin})")
                result.append(f"Rs2: {instruction[1]} (binary: {rs2_bin})")
                result.append(f"Imm: {instruction[2]}")
                result.append(f"\nMachine code for provided assembly code: {assembly_to_machine_Stype(inst.opcode, inst.funct3, instruction[1], instruction[2], instruction[3])}")
            elif inst.fmt == 'U':
                result.append("Given instruction is of U type.\n")
                result.append("U-type format: | imm[31:12] | rd | opcode |\n")
                result.append("               | 20 bits | 5 bits | 7 bits |\n")
                result.append("\nField Values:\n")
                result.append(f"Opcode: {inst.opcode}")
                rd_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                result.append(f"Rd: {instruction[1]} (binary: {rd_bin})")
                result.append(f"Imm: {instruction[2]}")
                result.append(f"\nMachine code for provided assembly code: {assembly_to_machine_Utype(inst.opcode, instruction[1], instruction[2])}")
            elif inst.fmt == 'SB':
                result.append("Given instruction is of SB type.\n")
                result.append("SB-type format: | imm[12|10:5] | rs2 | rs1 | funct3 | imm[4:1|11] | opcode |\n")
                result.append("                | 7 bits | 5 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                result.append("\nField Values:\n")
                result.append(f"Opcode: {inst.opcode}")
                result.append(f"Funct3: {inst.funct3}")
                rs1_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                rs2_bin = session.query(Regstore).filter(Regstore.regname == instruction[2]).first().binary
                result.append(f"Rs1: {instruction[1]} (binary: {rs1_bin})")
                result.append(f"Rs2: {instruction[2]} (binary: {rs2_bin})")
                result.append(f"Imm: {instruction[3]}")
                result.append(f"\nMachine code for provided assembly code: 0x{assembly_to_machine_SBtype(inst.opcode, inst.funct3, instruction[1], instruction[2], instruction[3])}")
            elif inst.fmt == 'UJ':
                result.append("Given instruction is of UJ type.\n")
                result.append("UJ-type format: | imm[20|10:1|11|19:12] | rd | opcode |\n")
                result.append("                | 20 bits | 5 bits | 7 bits |\n")
                result.append("\nField Values:\n")
                result.append(f"Opcode: {inst.opcode}")
                rd_bin = session.query(Regstore).filter(Regstore.regname == instruction[1]).first().binary
                result.append(f"Rd: {instruction[1]} (binary: {rd_bin})")
                result.append(f"Imm: {instruction[2]}")
                result.append(f"\nMachine code for provided assembly code: {assembly_to_machine_UJtype(inst.opcode, instruction[1], instruction[2])}")

            return jsonify({'result': '\n'.join(result)})

        elif choice == 2:
            try:
                binary = hex_to_binary(instruction)
                result = [f"Binary value: {binary}"]
                opcode = binary[-7:]
                inst = session.query(Inst).filter(Inst.opcode == opcode).first()

                if inst is None:
                    return jsonify({'result': 'Invalid Instruction'})

                if inst.fmt == 'R':
                    result.append("Given machine code is of R type.\n")
                    result.append("R-type format: | funct7 | rs2 | rs1 | funct3 | rd | opcode |\n")
                    result.append("              | 7 bits | 5 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {opcode} (Type: {inst.fmt})")
                    funct3 = binary[-15:-12]
                    result.append(f"Funct3: {funct3}")
                    funct7 = binary[-32:-25]
                    result.append(f"Funct7: {funct7}")
                    rd = binary[-12:-7]
                    rs1 = binary[-20:-15]
                    rs2 = binary[-25:-20]
                    result.append(f"Rd: {rd}")
                    result.append(f"Rs1: {rs1}")
                    result.append(f"Rs2: {rs2}")
                    result.append(f"\nAssembly code for provided machine code: {machine_to_assembly_Rtype(inst.opcode, funct3, funct7, rs1, rs2, rd).upper()}")
                elif inst.fmt == 'I':
                    rd = binary[-12:-7]
                    funct3 = binary[-15:-12]
                    rs1 = binary[-20:-15]
                    imm = binary[:-20]

                    if inst.instruction == 'fence' or inst.instruction == 'fence.i':
                        result.append("Given machine code is a fence instruction.\n")
                        result.append("Fence format: | imm[11:0] | rs1 | funct3 | rd | opcode |\n")
                        result.append("              | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                        result.append("\nField Values:\n")
                        result.append(f"Opcode: {opcode} ({inst.fmt})")
                        result.append(f"Funct3: {funct3}")
                        result.append(f"Assembly code for provided machine code: {machine_to_assembly_Fence(inst.opcode, funct3, imm).upper()}")
                    elif inst.instruction in ['csrrw', 'csrrs', 'csrrc']:
                        if(funct3[0] == '0'):
                            result.append("Given machine code is a CSR instruction.\n")
                            result.append("CSR format: | csr | rs1 | funct3 | rd | opcode |\n")
                            result.append("            | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                            result.append("\nField Values:\n")
                            result.append(f"Opcode: {opcode} ({inst.fmt})")
                            result.append(f"Funct3: {funct3}")
                            csr = imm[:12]
                            result.append(f"CSR: {csr}")
                            result.append(f"Rs1: {rs1}")
                            result.append(f"Rd: {rd}")
                            result.append(f"Assembly code for provided machine code: {machine_to_assembly_CSR(inst.opcode, funct3, csr, rs1, rd).upper()}")
                        else:
                            result.append("Given machine code is a CSR immediate instruction.\n")
                            result.append("CSR-I format: | csr | zimm | funct3 | rd | opcode |\n")
                            result.append("              | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                            result.append("\nField Values:\n")
                            result.append(f"Opcode: {opcode} ({inst.fmt})")
                            result.append(f"Funct3: {funct3}")
                            csr = imm[:12]
                            result.append(f"CSR: {csr}")
                            result.append(f"Zimm: {rs1}")
                            result.append(f"Rd: {rd}")
                            result.append(f"Assembly code for provided machine code: {machine_to_assembly_CSRI(inst.opcode, funct3, csr, rs1, rd).upper()}")
                    elif inst.instruction in ['ecall', 'ebreak']:
                        result.append("Given machine code is a system instruction.\n")
                        result.append("System format: | funct12 | rs1 | funct3 | rd | opcode |\n")
                        result.append("               | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                        result.append("\nField Values:\n")
                        result.append(f"Opcode: {opcode} ({inst.fmt})")
                        result.append(f"Funct3: {funct3}")
                        result.append(f"Assembly code for provided machine code: {machine_to_assembly_Sys(inst.opcode, funct3).upper()}")
                    else:
                        result.append("Given machine code is of I type.\n")
                        result.append("I-type format: | imm[11:0] | rs1 | funct3 | rd | opcode |\n")
                        result.append("               | 12 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                        result.append("\nField Values:\n")
                        result.append(f"Opcode: {opcode} ({inst.fmt})")
                        result.append(f"Funct3: {funct3}")
                        result.append(f"Imm: {imm}")
                        result.append(f"Rs1: {rs1}")
                        result.append(f"Rd: {rd}")
                        result.append(f"\nAssembly code for provided machine code: {machine_to_assembly_Itype(inst.opcode, funct3, rs1, imm, rd).upper()}")
                elif inst.fmt == 'S':
                    result.append("Given machine code is of S type.\n")
                    result.append("S-type format: | imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode |\n")
                    result.append("               | 7 bits | 5 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {opcode} ({inst.fmt})")
                    funct3 = binary[-15:-12]
                    result.append(f"Funct3: {funct3}")
                    rs1 = binary[-20:-15]
                    rs2 = binary[-25:-20]
                    imm = str(binary[-32:-25])+str(binary[-12:-7])
                    result.append(f"Imm[11:5]: {binary[-32:-25]}")
                    result.append(f"Imm[4:0]: {binary[-12:-7]}")
                    result.append(f"Rs1: {rs1}")
                    result.append(f"Rs2: {rs2}")
                    result.append(f"\nAssembly code for provided machine code: {machine_to_assembly_Stype(inst.opcode, funct3, rs2, imm, rs1).upper()}")
                elif inst.fmt == 'U':
                    result.append("Given machine code is of U type.\n")
                    result.append("U-type format: | imm[31:12] | rd | opcode |\n")
                    result.append("               | 20 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {opcode} ({inst.fmt})")
                    rd = binary[-12:-7]
                    imm = binary[:-12]
                    result.append(f"Rd: {rd}")
                    result.append(f"Imm: {imm}")
                    result.append(f"\nAssembly code for provided machine code: {machine_to_assembly_Utype(inst.opcode, rd, imm)}")
                elif inst.fmt == 'SB':
                    result.append("Given machine code is of SB type.\n")
                    result.append("SB-type format: | imm[12|10:5] | rs2 | rs1 | funct3 | imm[4:1|11] | opcode |\n")
                    result.append("                | 7 bits | 5 bits | 5 bits | 3 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {opcode} ({inst.fmt})")
                    funct3 = binary[-15:-12]
                    result.append(f"Funct3: {funct3}")
                    rs1 = binary[-20:-15]
                    rs2 = binary[-25:-20]
                    imm = binary[-31]+binary[-8]+binary[-30:-25]+binary[-12:-8]+'0'
                    result.append(f"Imm: {imm}")
                    result.append(f"Rs1: {rs1}")
                    result.append(f"Rs2: {rs2}")
                    result.append(f"\nAssembly code for provided machine code: {machine_to_assembly_SBtype(inst.opcode, funct3, rs1, rs2, imm)}")
                elif inst.fmt == 'UJ':
                    result.append("Given machine code is of UJ type.\n")
                    result.append("UJ-type format: | imm[20|10:1|11|19:12] | rd | opcode |\n")
                    result.append("                | 20 bits | 5 bits | 7 bits |\n")
                    result.append("\nField Values:\n")
                    result.append(f"Opcode: {opcode} ({inst.fmt})")
                    rd = binary[-12:-7]
                    imm = binary[-31]+binary[-20:-12]+binary[-21]+binary[-30:-21]+'00'
                    result.append(f"Rd: {rd}")
                    result.append(f"Imm: {imm}")
                    result.append(f"\nAssembly code for provided machine code: {machine_to_assembly_UJtype(inst.opcode, rd, imm)}")

                return jsonify({'result': '\n'.join(result)})

            except Exception as e:
                return jsonify({'result': f'Error processing machine code: {str(e)}'})

        return jsonify({'result': 'Invalid choice'})

    except Exception as e:
        return jsonify({'result': f'An error occurred: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)