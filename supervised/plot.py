import click
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def calc_precision_recall(n, confmat):
    tp = float(confmat[n][n])
    cond_positive = sum(confmat[n])
    test_positive = sum(confmat[i][n] for i in range(len(confmat)))

    precision = tp / cond_positive if cond_positive > 0 else 0
    recall = tp / test_positive if test_positive > 0 else 0

    return precision, recall


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
def precall(obj):
    for i in range(len(obj['confmat'])):
        p, r = calc_precision_recall(i, obj['confmat'])
        plt.plot(p, r, 'b+')
        plt.annotate(obj['labels'][i], xy=(p, r), xytext=(1, 1),
                     textcoords='offset points')

    plt.xlabel('Precision');
    plt.ylabel('Recall')
    plt.tight_layout(); plt.grid(); plt.show()


@plot.command()
@click.pass_obj
def confpr(obj):
    normalized = []
    for row in obj['confmat']:
        count = sum(row)
        normalized.append([float(x) / count if count > 0 else 0 for x in row])

    precisions, recalls = zip(*(calc_precision_recall(i, obj['confmat'])
                                for i in range(len(obj['confmat']))))

    fig, (ax1, ax2) = plt.subplots(1, 2)

    num_classes, width = len(obj['confmat']), 0.4
    ax1.set_title('Precision/Recall')
    ax1.bar([x - width for x in range(num_classes)], precisions, width,
            label='Precision', color='b')
    ax1.bar(range(num_classes), recalls, width, label='Recall', color='r')
    ax1.set_xticks(range(num_classes))
    ax1.set_xticklabels(obj['labels'], rotation=90)
    ax1.set_yticks([.0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.])
    ax1.set_xlim((-width, num_classes + width - 1))
    ax1.grid()
    ax1.legend()


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
