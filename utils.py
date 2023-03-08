import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


def read_file(input_filename):
    with open(input_filename, 'r') as f_in:
        lines = f_in.read().splitlines()

        w = int(lines[0])
        n = int(lines[1])

        x = []
        y = []

        circuits = []

        area = []
        max_area = 0

        for i in range(int(n)):
            split = lines[i + 2].split(' ')
            x.append(int(split[0]))
            y.append(int(split[1]))
            area.append(int(split[0]) * int(split[1]))
            circuits.append([x[i], y[i]])
            if area[i] >= max_area:
                max_area = area[i]
                index_max_area = i
        # compute a feasible approximation of l_max
        l_min = (sum(area)) // w
        l_max = sum(y)

        return w, n, x, y, l_min, l_max, index_max_area, circuits


def write_file(w, n, x, y, corners, length, num_instance, l_max, out_file, time, status):
    with open(out_file, 'w+') as f_out:

        f_out.write('{} {}\n'.format(w,length))
        f_out.write('{}\n'.format(n))

        for i in range(n):
            try:
                f_out.write('{} {} {} {} \n'.format(x[i], y[i], corners[i][0], corners[i][1]))
            except:
                f_out.write('{} {} \n'.format(x[i], y[i]))
        f_out.write('{} \n'.format(time))
        f_out.write('{}'.format(status))



def plot_solution(w_plate, h_plate, n, circuits, solution, save_fig_path, legend = True):
    """
    Show the given solution as a 2D plot.
    The solution should be a list of bottom left corners,
    contained in the given w_plate and h_plate marginse
    """
    assert(isinstance(w_plate, int))
    assert(isinstance(h_plate, int))
    assert(isinstance(circuits, list))
    assert(isinstance(n, int) and n == len(circuits))
    assert(isinstance(solution, dict))
    assert('corners' in solution)
    assert(len(circuits) == len(solution['corners']))

    corners = solution['corners']
    palette = matplotlib.colors.TABLEAU_COLORS

    # get n colors if they are not passed as parameter


    fig, ax = plt.subplots(facecolor='w', edgecolor='k')

    for i in range(n):
        # dimensions of the circuit
        x = circuits[i][0]
        y = circuits[i][1]


        r = Rectangle(
            corners[i],
            x,
            y,
            facecolor = np.random.rand(3,),
            edgecolor='black',
            label=f'circuit {i+1}'
        )
        ax.add_patch(r)

        # plot in each cell the id of the corresponding circuit if you do not want to visualize legend
        if not legend:
            rx, ry = r.get_xy()
            for j in range(r.get_width()):
                for k in range(r.get_height()):
                    cx = rx + j + 0.5
                    cy = ry + k + 0.5

                    ax.annotate(f'{i+1}', (cx, cy), color='black',
                                fontsize=8, ha='center', va='center')

    ax = plt.gca()
    ax.set_xlim(0, w_plate)
    ax.set_ylim(0, h_plate)
    ax.set_xticks(np.arange(w_plate))
    ax.set_yticks(np.arange(h_plate))
    ax.tick_params(labelsize = 4)
    plt.xlabel("width")
    plt.ylabel("height")
    plt.grid(color='black', linestyle='--')


    if legend:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    if save_fig_path is not None:
        plt.savefig(f"{save_fig_path}-sol.png", dpi=300, bbox_inches='tight')

    plt.close()
