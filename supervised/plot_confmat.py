import click
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


@click.command()
@click.argument('confusion-matrix', type=click.File('r'))
@click.option('--first-row', default=1)
@click.option('--last-row', default=-2)
@click.option('--first-col', default=1)
@click.option('--last-col', default=-4)
@click.option('--save', type=click.File('w'))
def main(confusion_matrix, first_row, first_col, last_row, last_col, save):
    data = [r[:-1].split(';') for r in confusion_matrix]

    confmat = [[int(x) if x else 0 for x in row[first_col:last_col]]
                       for row in data[first_row:last_row]]

    normalized = []
    for row in confmat:
        count = sum(row)
        normalized.append([float(x) / count if count > 0 else 0 for x in row])

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.set_title('Confusion Matrix')
    im1 = ax1.imshow(confmat, interpolation='nearest')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    ax2.set_title('Normalized Confusion Matrix')
    im2 = ax2.imshow(normalized, interpolation='nearest')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.show()
    

if __name__ == '__main__':
    main()
