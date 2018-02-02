import os

examples = ['common_emitter', 'joule_thief', 'mcu', 'sallen_key']


def build_dir_path(example):
    return os.path.join(example, 'build')


def file_path(example, file):
    return os.path.join(example, file)


def build_file_path(example, file):
    return os.path.join(build_dir_path(example), file)


def build(path):
    os.system('python3 %s' % path)


def clean(path):
    os.system('rm -rf %s' % path)


def open_svg(path):
    os.system('chromium %s &' % path)


if __name__ == '__main__':
    clean('build')
    for example in examples:
        print('Building', example)
        build(file_path(example, example + '.py'))
