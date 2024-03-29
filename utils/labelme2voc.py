#!/usr/bin/env python

from __future__ import print_function

import argparse
import glob
import json
import os
import os.path as osp
import sys

import numpy as np
import PIL.Image
from shutil import rmtree
import labelme


def convert_to_voc(input_dir, output_dir_path, labels_file):
    output_dir = output_dir_path+'/voc_data'
    if osp.exists(output_dir):
        rmtree(output_dir)
    os.makedirs(output_dir)
    os.makedirs(osp.join(output_dir, 'JPEGImages'))
    os.makedirs(osp.join(output_dir, 'SegmentationClass'))
    os.makedirs(osp.join(output_dir, 'SegmentationClassPNG'))
    os.makedirs(osp.join(output_dir, 'SegmentationClassVisualization'))
    print('Creating dataset:', output_dir)

    class_names = []
    class_name_to_id = {}
    for i, line in enumerate(open(labels_file).readlines()):
        class_id = i - 1  # starts with -1
        class_name = line.strip()
        class_name_to_id[class_name] = class_id
        if class_id == -1:
            assert class_name == '__ignore__'
            continue
        elif class_id == 0:
            assert class_name == '_background_'
        class_names.append(class_name)
    
    class_names = tuple(class_names)
    print('class_names:', class_names)
    out_class_names_file = osp.join(output_dir, 'class_names.txt')
    with open(out_class_names_file, 'w') as f:
        f.writelines('\n'.join(class_names))
    print('Saved class_names:', out_class_names_file)

    # colormap = labelme.utils.label_colormap(255)
    colormap = np.array([(0, 0, 0), (0, 0, 1), (0, 1, 0)])

    for label_file in glob.glob(osp.join(input_dir, '*.json')):
        print('Generating dataset from:', label_file)
        with open(label_file) as f:
            base = osp.splitext(osp.basename(label_file))[0]
            out_img_file = osp.join(
                output_dir, 'JPEGImages', base + '.jpg')
            out_lbl_file = osp.join(
                output_dir, 'SegmentationClass', base + '.npy')
            out_png_file = osp.join(
                output_dir, 'SegmentationClassPNG', base + '.png')
            out_viz_file = osp.join(
                output_dir,
                'SegmentationClassVisualization',
                base + '.jpg',
            )

            data = json.load(f)

            img_file = osp.join(osp.dirname(label_file), data['imagePath'])
            img = np.asarray(PIL.Image.open(img_file))
            PIL.Image.fromarray(img).save(out_img_file)

            cls, ins = labelme.utils.shapes_to_label(
                img_shape=img.shape,
                shapes=data['shapes'],
                label_name_to_value=class_name_to_id,
            )
            ins[cls == -1] = 0 
            #lbl = np.array(lbl)
            labelme.utils.lblsave(out_png_file, cls)

            np.save(out_lbl_file, cls)

            # viz = labelme.utils.(
            #     lbl, img, class_names, colormap=colormap)
            # PIL.Image.fromarray(viz).save(out_viz_file)


# def main():
#     parser = argparse.ArgumentParser(
#         formatter_class=argparse.ArgumentDefaultsHelpFormatter
#     )
#     parser.add_argument('input_dir', help='input annotated directory')
#     parser.add_argument('output_dir', help='output dataset directory')
#     parser.add_argument('--labels', help='labels file', required=True)
#     parser.add_argument(
#         '--noviz', help='no visualization', action='store_true'
#     )
#     args = parser.parse_args()
#
#     if osp.exists(args.output_dir):
#         print('Output directory already exists:', args.output_dir)
#         sys.exit(1)
#     os.makedirs(args.output_dir)
#     os.makedirs(osp.join(args.output_dir, 'JPEGImages'))
#     os.makedirs(osp.join(args.output_dir, 'SegmentationClass'))
#     os.makedirs(osp.join(args.output_dir, 'SegmentationClassPNG'))
#     if not args.noviz:
#         os.makedirs(
#             osp.join(args.output_dir, 'SegmentationClassVisualization')
#         )
#     os.makedirs(osp.join(args.output_dir, 'SegmentationObject'))
#     os.makedirs(osp.join(args.output_dir, 'SegmentationObjectPNG'))
#     if not args.noviz:
#         os.makedirs(
#             osp.join(args.output_dir, 'SegmentationObjectVisualization')
#         )
#     print('Creating dataset:', args.output_dir)
#
#     class_names = []
#     class_name_to_id = {}
#     for i, line in enumerate(open(args.labels).readlines()):
#         class_id = i - 1  # starts with -1
#         class_name = line.strip()
#         class_name_to_id[class_name] = class_id
#         if class_id == -1:
#             assert class_name == '__ignore__'
#             continue
#         elif class_id == 0:
#             assert class_name == '_background_'
#         class_names.append(class_name)
#     class_names = tuple(class_names)
#     print('class_names:', class_names)
#     out_class_names_file = osp.join(args.output_dir, 'class_names.txt')
#     with open(out_class_names_file, 'w') as f:
#         f.writelines('\n'.join(class_names))
#     print('Saved class_names:', out_class_names_file)
#
#     for label_file in glob.glob(osp.join(args.input_dir, '*.json')):
#         print('Generating dataset from:', label_file)
#         with open(label_file) as f:
#             base = osp.splitext(osp.basename(label_file))[0]
#             out_img_file = osp.join(
#                 args.output_dir, 'JPEGImages', base + '.jpg')
#             out_cls_file = osp.join(
#                 args.output_dir, 'SegmentationClass', base + '.npy')
#             out_clsp_file = osp.join(
#                 args.output_dir, 'SegmentationClassPNG', base + '.png')
#             if not args.noviz:
#                 out_clsv_file = osp.join(
#                     args.output_dir,
#                     'SegmentationClassVisualization',
#                     base + '.jpg',
#                 )
#             out_ins_file = osp.join(
#                 args.output_dir, 'SegmentationObject', base + '.npy')
#             out_insp_file = osp.join(
#                 args.output_dir, 'SegmentationObjectPNG', base + '.png')
#             if not args.noviz:
#                 out_insv_file = osp.join(
#                     args.output_dir,
#                     'SegmentationObjectVisualization',
#                     base + '.jpg',
#                 )
#
#             data = json.load(f)
#
#             img_file = osp.join(osp.dirname(label_file), data['imagePath'])
#             img = np.asarray(PIL.Image.open(img_file))
#             PIL.Image.fromarray(img).save(out_img_file)
#
#             cls, ins = labelme.utils.shapes_to_label(
#                 img_shape=img.shape,
#                 shapes=data['shapes'],
#                 label_name_to_value=class_name_to_id,
#                 type='instance',
#             )
#             ins[cls == -1] = 0  # ignore it.
#
#             # class label
#             labelme.utils.lblsave(out_clsp_file, cls)
#             np.save(out_cls_file, cls)
#             if not args.noviz:
#                 clsv = imgviz.label2rgb(
#                     label=cls,
#                     img=imgviz.rgb2gray(img),
#                     label_names=class_names,
#                     font_size=15,
#                     loc='rb',
#                 )
#                 imgviz.io.imsave(out_clsv_file, clsv)
#
#             # instance label
#             labelme.utils.lblsave(out_insp_file, ins)
#             np.save(out_ins_file, ins)
#             if not args.noviz:
#                 instance_ids = np.unique(ins)
#                 instance_names = [str(i) for i in range(max(instance_ids) + 1)]
#                 insv = imgviz.label2rgb(
#                     label=ins,
#                     img=imgviz.rgb2gray(img),
#                     label_names=instance_names,
#                     font_size=15,
#                     loc='rb',
#                 )
#                 imgviz.io.imsave(out_insv_file, insv)


# if __name__ == '__main__':
#     main()
