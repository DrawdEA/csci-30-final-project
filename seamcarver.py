#!/usr/bin/env python3

from PIL import Image
from picture import Picture
import math

class SeamCarver(Picture):
    ## TO-DO: fill in the methods below
    def energy(self, i: int, j: int) -> float:
        '''
        Return the energy of pixel at column i and row j
        '''

        '''
        Since there is no pixel (i, j−1) we wrap around and use the corresponding pixel from the bottom
        row of the image, thus performing calculations based on pixel (i, j + 1) and pixel (i, H − 1).
        '''
        #edges
        w, h = self._width, self._height

        row_1 = self[(i + 1) % w, j]
        row_2 = self[(i - 1) % w, j]
        col_1 = self[i, (j + 1) % h]
        col_2 = self[i, (j - 1) % h]

        R_x = row_1[0] - row_2[0]
        G_x = row_1[1] - row_2[1]
        B_x = row_1[2] - row_2[2]

        R_y = col_1[0] - col_2[0]
        G_y = col_1[1] - col_2[1]
        B_y = col_1[2] - col_2[2]

        xHorizontal = (R_x)**2 + (G_x)**2 + (B_x)**2
        yHorizontal = (R_y)**2 + (G_y)**2 + (B_y)**2

        return math.sqrt(xHorizontal + yHorizontal)

    def find_vertical_seam(self) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        vertical seam
        '''
        width, height = self._width, self._height

        # make table of energies
        energies = {}
        for i in range(width):
            for j in range(height):
                energies[i, j] = {"energy": self.energy(i, j), "total": None, "prev": None}  # {"energy": static pixel energy, "total": cumulative DP energy, "prev": previous column index for backtracking}

        # set starting total of top row
        for i in range(width):
            energies[i, 0]["total"] = energies[i, 0]["energy"]

        # get accumulated energy per layer
        for j in range(1, height):
            for i in range(width):
                #check above, above-left, above-right
                to_check = []
                to_check.append((i, j-1))
                if i > 0:
                    to_check.append((i-1, j-1))
                if i < width - 1:
                    to_check.append((i+1, j-1))

                best_prev = None
                best_energy = 1e20
                # from checkable vertices, get smallest possible path so far
                for (pi, pj) in to_check:
                    total_prev = energies[pi, pj]["total"]
                    if total_prev < best_energy:
                        best_energy = total_prev
                        best_prev = pi

                # track current total energy and path taken so far
                energies[i, j]["total"] = energies[i, j]["energy"] + best_energy
                energies[i, j]["prev"] = best_prev

        # find min-energy end point (bottom row)
        min_i = 0
        # use bottom left as default minimum index
        min_total = energies[0, height-1]["total"]

        # scan bottom row for smallest total
        for i in range(1, width):
            total = energies[i, height-1]["total"]
            if total < min_total:
                min_total = total
                min_i = i

        # backtrack to get cols
        seam = []
        col = min_i

        for j in reversed(range(height)):
            seam.append(col)
            col = energies[col, j]["prev"]

        seam.reverse()
        return seam

    def find_horizontal_seam(self) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        horizontal seam
        '''
        img = self.picture()
        transposed_img = SeamCarver(img.transpose(Image.ROTATE_270))
        vertical_seam = transposed_img.find_vertical_seam() 
        horizontal_seam = []
        for i in vertical_seam:
            horizontal_seam.append(self._height - i)
        return horizontal_seam

    def remove_vertical_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''
        for j in range(self._height):
                for i in range(seam[j], self._width-1):
                    self[i,j] = self[i+1, j]
                del(self[self._width-1, j])
        self._width-=1

    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a horizontal seam from the picture
        '''
        img = self.picture()

        # transpose image to vertical seam
        transposed_img = SeamCarver(img.transpose(Image.ROTATE_270))

        # remove vertical seam and transpose back to horizontal seam
        transposed_img.remove_vertical_seam([self._height - j for j in seam])
        result_carver = SeamCarver(transposed_img.picture().transpose(Image.ROTATE_90))

        # update self with result
        self.clear()
        self.update(result_carver)
        self._width, self._height = result_carver._width, result_carver._height

class SeamError(Exception):
    pass
