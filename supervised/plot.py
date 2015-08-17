import click
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def calc_tpr_fpr(n, confmat):
    tp = confmat[n][n]
    fp = sum(x for x in confmat[n]) - tp
    p = sum(confmat[i][n] for i in range(len(confmat)))
    n = sum(sum(row) for row in confmat) - p

    return float(tp) / p if p > 0 else 0, float(fp) / n if n > 0 else 0


@click.group()
@click.argument('confusion-matrix', type=click.File('r'))
@click.option('--first-row', default=1,
              help='First row of the confusion matrix (labels excluded)')
@click.option('--last-row', default=-2,
              help='Last row of the confusion matrix')
@click.option('--first-col', default=1,
              help='First column of the confusion matrix (labels excluded)')
@click.option('--last-col', default=-4,
              help='Last column of the confusion matrix')
@click.pass_obj
def plot(obj, confusion_matrix, first_row, first_col, last_row, last_col):
    data = [r[:-1].decode('utf8').split(';') for r in confusion_matrix]
    obj['confmat']= [[int(x) if x else 0 for x in row[first_col:last_col]]
                             for row in data[first_row:last_row]]
    obj['labels'] = data[first_row-1][first_col:last_col]


@plot.command()
@click.pass_obj
def roc(obj):
    for i in range(len(obj['confmat'])):
        tpr, fpr = calc_tpr_fpr(i, obj['confmat'])
        plt.plot(fpr, tpr, 'b+')
        plt.annotate(obj['labels'][i], xy=(fpr, tpr), xytext=(1, 1),
                     textcoords='offset points')

    plt.plot([0., 1.], [0., 1.], 'b--')
    plt.xlabel('False Positive Ratio (FP / N)');
    plt.ylabel('True Positive Ratio (TP / P)')
    plt.tight_layout(); plt.grid(); plt.show()


@plot.command()
@click.pass_obj
def confusion_matrix(obj):
    normalized = []
    for row in obj['confmat']:
        count = sum(row)
        normalized.append([float(x) / count if count > 0 else 0 for x in row])

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.set_title('Confusion Matrix')
    ax1.set_xlabel('Actual Class'); ax1.set_ylabel('Predicted Class')
    ax1.set_xticks(range(len(obj['labels'])))
    ax1.set_xticklabels(obj['labels'], rotation=90)
    ax1.set_yticks(range(len(obj['labels'])))
    ax1.set_yticklabels(obj['labels'])
    im1 = ax1.imshow(obj['confmat'], interpolation='nearest')
    plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)

    ax2.set_title('Normalized Confusion Matrix')
    ax2.set_xlabel('Actual Class'); ax2.set_ylabel('Predicted Class')
    ax2.set_xticks(range(len(obj['labels'])))
    ax2.set_xticklabels(obj['labels'], rotation=90)
    ax2.set_yticklabels(obj['labels'])
    ax2.set_yticks(range(len(obj['labels'])))
    im2 = ax2.imshow(normalized, interpolation='nearest')
    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.show()
    

if __name__ == '__main__':
    plot(obj={})
