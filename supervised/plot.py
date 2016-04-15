import click
import matplotlib as mpl


def calc_precision_recall(n, confmat):
    """ calculates precision and recall for class n given the confusion matrix """
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
@click.option('--latex/--show')
@click.option('--hide-o/--show-o')
@click.pass_obj
def plot(obj, confusion_matrix, first_row, first_col, last_row, last_col, latex, hide_o):
    """ graphical plots of some classification related metrics """
    data = [r[:-1].decode('utf8').split(';') for r in confusion_matrix]
    obj['confmat']= [[int(x) if x else 0 for x in row[first_col:last_col]]
                             for row in data[first_row:last_row]]
    obj['labels'] = data[first_row-1][first_col:last_col]
    obj['hide_o'] = hide_o
    obj['latex'] = latex
    if latex:
        mpl.use("pgf")  # Matplotlib setup for LaTeX plots generation
        mpl.rcParams.update({
            "pgf.texsystem": "pdflatex",
            "font.family": "serif",
            "font.serif": [],                   # use latex default serif font
        })


@plot.command()
@click.pass_obj
def precall_scatter(obj):
    """ precision-recall plot """
    import matplotlib.pyplot as plt

    for i in range(len(obj['confmat'])):
        p, r = calc_precision_recall(i, obj['confmat'])
        plt.plot(p, r, 'b+')
        plt.annotate(obj['labels'][i], xy=(p, r), xytext=(1, 1),
                     textcoords='offset points')

    plt.xlabel('Precision');
    plt.ylabel('Recall')
    plt.grid()
    plt.tight_layout()

    if obj['latex']:
        plt.savefig('precall_scatter.pdf')
    else:
        plt.show()


@plot.command()
@click.pass_obj
def precall_bars(obj):
    """ plots precision/recall bars for each class """
    import matplotlib.pyplot as plt

    normalized = []
    for row in obj['confmat']:
        count = sum(row)
        normalized.append([float(x) / count if count > 0 else 0 for x in row])

    precisions, recalls = zip(*(calc_precision_recall(i, obj['confmat'])
                                for i in range(len(obj['confmat']))))
    num_classes, width = len(obj['confmat']), 0.4

    if obj['hide_o']:
        o_index = obj['labels'].index('O')
        obj['labels'].remove('O')
        recalls = recalls[:o_index] + recalls[o_index + 1:]
        precisions = precisions[:o_index] + precisions[o_index + 1:]
        num_classes -= 1

    fig, ax1 = plt.subplots(1, 1)
    ax1.bar([x - width for x in range(num_classes)], precisions, width,
            label='Precision', color='b')
    ax1.bar(range(num_classes), recalls, width, label='Recall', color='r')
    ax1.set_xticks(range(num_classes))
    ax1.set_xticklabels(obj['labels'], rotation=90)
    ax1.set_yticks([.0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.])
    ax1.set_xlim((-width, num_classes + width - 1))
    ax1.grid()
    ax1.legend()
    plt.tight_layout()

    if obj['latex']:
        plt.savefig('precall_bars.pdf')
    else:
        plt.show()


@plot.command()
@click.option('--normalized', '-n', is_flag=True)
@click.pass_obj
def confmat(obj, normalized):
    """ plots the confusion matrix """
    import matplotlib.pyplot as plt

    if normalized:
        matrix = []
        for row in obj['confmat']:
            count = sum(row)
            matrix.append([float(x) / count if count > 0 else 0 for x in row])
    else:
        matrix = obj['confmat']

    if obj['hide_o']:
        o_index = obj['labels'].index('O')
        obj['labels'].remove('O')
        new_matrix = []
        for i, row in enumerate(matrix):
            if i != o_index:
                new_matrix.append([x for j, x in enumerate(row)
                                     if j != o_index])
        matrix = new_matrix

    fig, ax1 = plt.subplots(1, 1)
    ax1.set_xlabel('Actual Class'); ax1.set_ylabel('Predicted Class')
    ax1.set_xticks(range(len(obj['labels'])))
    ax1.set_xticklabels(obj['labels'], rotation=90)
    ax1.set_yticklabels(obj['labels'])
    ax1.set_yticks(range(len(obj['labels'])))
    im2 = ax1.imshow(matrix, interpolation='nearest')
    plt.colorbar(im2, ax=ax1, fraction=0.046, pad=0.04)
    plt.tight_layout()

    if obj['latex']:
        plt.savefig('confmat.pdf')
    else:
        plt.show()
    

if __name__ == '__main__':
    plot(obj={})
