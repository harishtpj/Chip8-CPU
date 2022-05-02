from chip8_cpu import Chip8CPU
import sys, pygame
from pygame import Rect

pygame.init()

class Chip8Emulator:
    def __init__(self, fname):
        self.exec(fname)
    
    def _setup_graphics(self, screen):
        screen.fill((0,0,0))
    
    def _draw_graphics(self, screen, colors, cpu, width, height):
        for x in range(width):
            for y in range(height):
                screen.fill(colors[cpu.graphics[x + (y * width)]], Rect(x*10, y*10, 10, 10))
        
        pygame.display.flip()
        cpu.draw_flag = False
    
    def _get_key_event(self, events, keys, cpu):
        for event in events:
            event_type = -1
            if event.type == pygame.KEYDOWN:
                event_type = 1
            elif event.type == pygame.KEYUP:
                event_type = 0
            elif event.type == pygame.QUIT:
                sys.exit(0)
            
            if event_type == 0 or event_type == 1:
                if event.key in keys:
                    i = keys.index(event.key)
                    cpu.keys[i] = event_type
    
    def exec(self, fname):
        keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_r,
                pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_f,
                pygame.K_z, pygame.K_x, pygame.K_c, pygame.K_v]
        chip8_cpu = Chip8CPU()

        black = (0, 0, 0)
        white = (255, 255, 255)
        colors = [black, white]
        width = 64
        height = 32
        size = (width * 10, height * 10)
        pixels = width * height

        screen = pygame.display.set_mode(size)
        self._setup_graphics(screen)

        chip8_cpu.init(pixels)
        chip8_cpu.load_rom(fname)

        # Main Emulation Cycle
        while True:
            chip8_cpu.execute()

            if chip8_cpu.draw_flag:
                self._draw_graphics(screen, colors, chip8_cpu, width, height)
            
            events = pygame.event.get()
            self._get_key_event(events, keys, chip8_cpu)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Error: Requires Script And Game.\n")
        sys.exit(-1)
    else:
        fname = sys.argv[1]
        Chip8Emulator(fname)