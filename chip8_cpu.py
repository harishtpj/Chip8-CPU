import sys
from random import randint, seed
from time import time

class Chip8CPU:
    def __init__(self):
        self.fontset = [0xF0, 0x90, 0x90, 0x90, 0xF0, 
                        0x20, 0x60, 0x20, 0x20, 0x70, 
                        0xF0, 0x10, 0xF0, 0x80, 0xF0, 
                        0xF0, 0x10, 0xF0, 0x10, 0xF0, 
                        0x90, 0x90, 0xF0, 0x10, 0x10, 
                        0xF0, 0x80, 0xF0, 0x10, 0xF0, 
                        0xF0, 0x80, 0xF0, 0x90, 0xF0, 
                        0xF0, 0x10, 0x20, 0x40, 0x40, 
                        0xF0, 0x90, 0xF0, 0x90, 0xF0, 
                        0xF0, 0x90, 0xF0, 0x10, 0xF0, 
                        0xF0, 0x90, 0xF0, 0x90, 0x90, 
                        0xE0, 0x90, 0xE0, 0x90, 0xE0, 
                        0xF0, 0x80, 0x80, 0x80, 0xF0, 
                        0xE0, 0x90, 0x90, 0x90, 0xE0, 
                        0xF0, 0x80, 0xF0, 0x80, 0xF0, 
                        0xF0, 0x80, 0xF0, 0x80, 0x80]
    
    def init(self, pixels):
        seed()

        self.stack = []
        self.memory = [0] * 4096
        self.registers = [0] * 16
        self.keys = [0] * 16

        self.opcode = 0
        self.PC = 0x200
        self.I = 0
        self.SP = -1
        self.pixels = pixels
        self.graphics = [0] * pixels
        self.t_last = time()
        self.DT = 0
        self.ST = 0
        self.draw_flag = True

        for i in range(80):
            self.memory[i] = self.fontset[i]
    
    def load_rom(self, fname):
        with open(fname, "rb") as fp:
            byte = fp.read()
            for i in range(len(byte)):
                self.memory[self.PC + i] = byte[i]
    
    def execute(self):
        self.opcode = self.memory[self.PC] << 8 | self.memory[self.PC + 1]

        Vx = (self.opcode & 0x0F00) >> 8
        Vy = (self.opcode & 0x00F0) >> 4

        # Instructions with pattern 0---
        if self.opcode & 0xF000 == 0x0000:
            #00E0 - CLS => Clears Screen
            if self.opcode == 0x00E0:
                self.graphics = [0] * self.pixels
            
            #00EE - RET => Returns from Subroutine
            elif self.opcode == 0x00EE:
                self.PC = self.stack.pop()
            
            #0NNN - SYS addr => Execute machine language routine
            elif self.opcode & 0x0F00 != 0x0000:
                self.PC = (self.opcode & 0x0FFF) - 2
            
            #Not Found
            else:
                self.PC -= 2

        #1NNN - JP addr  => Jump      
        elif self.opcode & 0xF000 == 0x1000:
            self.PC = (self.opcode & 0x0FFF) - 2
        
        #2NNN - CALL addr  => Execute machine language routinePermalink 
        elif self.opcode & 0xF000 == 0x2000:
            self.stack.append(self.PC)
            self.PC = (self.opcode & 0x0FFF) - 2

        #3XNN - SE Vx, byte  => Skip
        elif self.opcode & 0xF000 == 0x3000:
            if self.registers[Vx] == self.opcode & 0x00FF:
                self.PC += 2
        
        #4XNN - SNE Vx, byte  => Skip    
        elif self.opcode & 0xF000 == 0x4000:
            if self.registers[Vx] != self.opcode & 0x00FF:
                self.PC += 2
        
        #5XY0 - SE Vx, Vy  => Skip 
        elif self.opcode & 0xF000 == 0x5000:
            if self.registers[Vx] == self.registers[Vy]:
                self.PC += 2
        
        #6XNN - LD Vx, byte  => Set 
        elif self.opcode & 0xF000 == 0x6000:
            self.registers[Vx] = self.opcode & 0x00FF
        
        #7XNN - ADD Vx, byte  => Add
        elif self.opcode & 0xF000 == 0x7000:
            self.registers[Vx] += self.opcode & 0x00FF
            self.registers[Vx] &= 0xFF

        # Instructions with pattern 8---
        elif self.opcode & 0xF000 == 0x8000:
            l = self.opcode & 0x000F

            #8XY0 - LD Vx, Vy  => Set   
            if l == 0x0000:
                self.registers[Vx] = self.registers[Vy]
            
            #8XY1 - OR Vx, Vy  => Binary OR   
            elif l == 0x0001:
                self.registers[Vx] = self.registers[Vx] | self.registers[Vy]
            
            #8XY2 - AND Vx, Vy  =>  Binary AND  
            elif l == 0x0002:
                self.registers[Vx] = self.registers[Vx] & self.registers[Vy]

            #8XY3 - XOR Vx, Vy  =>  Logical XOR  
            elif l == 0x0003:
                self.registers[Vx] = self.registers[Vx] ^ self.registers[Vy]
            
            #8XY4 - ADD Vx, Vy  =>  Add
            elif l == 0x0004:
                self.registers[Vx] += self.registers[Vy]
                self.registers[0xF] = 1 if self.registers[Vx] > 0xFF else 0
                self.registers[Vx] &= 0xFF

            #8XY5 - SUB Vx, Vy  =>  Subtract
            elif l == 0x0005:
                self.registers[0xF] = 0 if self.registers[Vx] < self.registers[Vy] else 1
                self.registers[Vx] -= self.registers[Vy]
                self.registers[Vx] &= 0xFF
            
            #8XY6 - SHR Vx {, Vy}  =>  Shift
            elif l == 0x0006:
                self.registers[0xF] = self.registers[Vx] & 0x01
                self.registers[Vx] = self.registers[Vx] >> 1
            
            #8XY7 - SUBN Vx, Vy  =>  Subtract
            elif l == 0x0007:
                self.registers[0xF] = 0 if self.registers[Vx] > self.registers[Vy] else 1
                self.registers[Vx] = self.registers[Vy] - self.registers[Vx]
                self.registers[Vx] &= 0xFF
            
            #8XYE - SHL Vx {, Vy}  =>  Shift
            elif l == 0x000E:
                self.registers[0xF] = self.registers[Vx] & 0x80
                self.registers[Vx] = self.registers[Vx] << 1
            
            #Not Found
            else:
                self.PC -= 2
        
        #9XY0 - SNE Vx, Vy  => Skip
        elif self.opcode & 0xF000 == 0x9000:
            if self.registers[Vx] != self.registers[Vy]:
                self.PC += 2
        
        #ANNN - LD I, addr  => Set index
        elif self.opcode & 0xF000 == 0xA000:
            self.I = self.opcode & 0x0FFF
        
        #BNNN - JP V0, addr  => Jump with offset
        elif self.opcode & 0xF000 == 0xB000:
            self.PC = (self.opcode & 0x0FFF) + self.registers[0x0] - 2
        
        #CXNN - RND Vx, byte  => Random
        elif self.opcode & 0xF000 == 0xC000:
            rand_int = randint(0, 0xFF)
            self.registers[Vx] = rand_int & (self.opcode & 0x00FF)
        
        #DXYN - DRW Vx, Vy, nibble  => Display
        elif self.opcode & 0xF000 == 0xD000:
            xcord = self.registers[Vx]
            ycord = self.registers[Vy]
            height = self.opcode & 0x000F
            pixel = 0
            self.registers[0xF] = 0

            for y in range(height):
                pixel = self.memory[self.I + y]
                for x in range(8):
                    i = xcord + x + ((y + ycord) * 64)
                    if pixel & (0x80 >> x) != 0 and not (y + ycord  >= 32 or x + xcord >= 64):
                        if self.graphics[i] == 1:
                            self.registers[0xF] = 1
                        self.graphics[i] ^= 1
            
            self.draw_flag = True
        
        # Instructions with pattern E---
        elif self.opcode & 0xF000 == 0xE000:
            #EX9E - SKP Vx  => Skip if key
            if self.opcode & 0x00FF == 0x009E:
                if self.keys[self.registers[Vx]] == 1:
                    self.PC += 2
            
            #EXA1 - SKNP Vx  => Skip if key
            elif self.opcode & 0x00FF == 0x00A1:
                if self.keys[self.registers[Vx]] == 0:
                    self.PC += 2
            
            #Not Found
            else:
                self.PC -= 2
        
        # Instructions with pattern F---
        elif self.opcode & 0xF000 == 0xF000:
            nn = self.opcode & 0x00FF

            #FX07 - LD Vx, DT  => Timers   
            if nn == 0x0007:
                self.registers[Vx] = self.DT
            
            #FX0A - LD Vx, K  => Get key   
            elif nn == 0x000A:
                key = -1
                for i in range(len(self.keys)):
                    if self.keys[i] == 1:
                        key = i
                        break
                    if key >= 0:
                        self.registers[Vx] = key
                    else:
                        self.PC -= 2
            
            #FX15 - LD DT, Vx  => Timers   
            elif nn == 0x0015:
                self.DT = self.registers[Vx]
            
            #FX18 - LD ST, Vx  => Timers   
            elif nn == 0x0018:
                self.ST = self.registers[Vx]
            
            #FX1E - ADD I, Vx  => Add to index   
            elif nn == 0x001E:
                self.I += self.registers[Vx]
            
            #FX29 - LD F, Vx  => Font character   
            elif nn == 0x0029:
                self.I = self.registers[Vx] * 5
            
            #FX33 - LD B, Vx  => Binary-coded decimal conversion   
            elif nn == 0x0033:
                self.memory[self.I] = self.registers[Vx] // 100
                self.memory[self.I + 1] = (self.registers[Vx] // 10) % 10
                self.memory[self.I + 2] = (self.registers[Vx] % 100) % 10
            
            #FX55 - LD [I], Vx  => Store and load memory   
            elif nn == 0x0055:
                for n in range(Vx + 1):
                    self.memory[self.I + n] = self.registers[n]

            #FX65 - LD Vx, [I]  => Store and load memory   
            elif nn == 0x0065:
                for n in range(Vx + 1):
                    self.registers[n] = self.memory[self.I + n]
            
            #Not Found
            else:
                self.PC -= 2

        # Not currently made print
        else:
            print(hex(self.opcode))
            self.PC -= 2
        
        self.PC += 2

        pytime = time()
        if pytime - self.t_last >= 1.0/60:
            if self.DT > 0:
                self.DT -= 1
            
            if self.ST > 0:
                sys.stdout.write("\a")
                self.ST -= 1
            
            self.t_last = pytime
