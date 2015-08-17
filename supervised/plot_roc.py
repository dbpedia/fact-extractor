import click
import matplotlib.pyplot as plt


def calc_tpr_fpr(n, confmat):
    tp = confmat[n][n]
    fp = sum(x for x in confmat[n]) - tp
    p = sum(confmat[i][n] for i in range(len(confmat)))
    n = sum(sum(row) for row in confmat) - p

    return float(tp) / p if p > 0 else 0, float(fp) / n if n > 0 else 0


@click.command()
@click.argument('confusion-matrix', type=click.File('r'))
@click.option('--first-row', default=1)
@click.option('--last-row', default=-2)
@click.option('--first-col', default=1)
@click.option('--last-col', default=-4)
def main(confusion_matrix, first_row, first_col, last_row, last_col):
    data = [r[:-1].decode('utf8').split(';') for r in confusion_matrix]
    confmat = [[int(x) if x else 0 for x in row[first_col:last_col]]
                       for row in data[first_row:last_row]]
    labels = data[first_row-1][first_col:last_col]

    for i in range(len(confmat)):
        tpr, fpr = calc_tpr_fpr(i, confmat)
        plt.plot(fpr, tpr, 'b+')
        plt.annotate(labels[i], xy=(fpr, tpr), xytext=(1, 1),
                     textcoords='offset points')

    plt.plot([0., 1.], [0., 1.], 'b--')
    plt.xlabel('False Positive Ratio (FP / N)');
    plt.ylabel('True Positive Ratio (TP / P)')
    plt.grid(); plt.show()

if __name__ == '__main__':
    main()
