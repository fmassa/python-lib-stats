# Python Library stats

This is a small library that allows you to query some useful statistics for Python code-bases.
We currently report library imports, function calls and attributes.

## Usage


In order to find all uses (imports / function calls / attribute queries) from library `<mylib>` over codebase `<path/to/python/repo>`, run the following command:

```
python main.py --local_dir <path/to/python/repo> --library_name <mylib>
```

## Example

Looking for all `torchvision` occurrences on the [DETR](https://github.com/facebookresearch/detr) codebase yields:

```
===========================================================================
                                  Imports
===========================================================================
                                                                    | Count
---------------------------------------------------------------------------
    torchvision                                                     : 4
    torchvision.ops._new_empty_tensor                               : 1
    torchvision.ops.misc._output_size                               : 1
    torchvision.ops.boxes.box_area                                  : 1
    torchvision.transforms                                          : 1
    torchvision.transforms.functional                               : 1
    torchvision.models._utils.IntermediateLayerGetter               : 1
===========================================================================
                                   Calls
===========================================================================
                                                                    | Count
---------------------------------------------------------------------------
    torchvision.__version__.split                                   : 2
    torchvision.ops.boxes.box_area                                  : 2
    torchvision.transforms.RandomCrop.get_params                    : 2
    torchvision._is_tracing                                         : 1
    torchvision.ops.misc._output_size                               : 1
    torchvision.ops._new_empty_tensor                               : 1
    torchvision.ops.misc.interpolate                                : 1
    torchvision.transforms.functional.crop                          : 1
    torchvision.transforms.functional.hflip                         : 1
    torchvision.transforms.functional.resize                        : 1
    torchvision.transforms.functional.pad                           : 1
    torchvision.transforms.functional.to_tensor                     : 1
    torchvision.transforms.RandomErasing                            : 1
    torchvision.transforms.functional.normalize                     : 1
    torchvision.models._utils.IntermediateLayerGetter               : 1
    torchvision.models.{?}                                          : 1
===========================================================================
                                   Attrs
===========================================================================
                                                                    | Count
---------------------------------------------------------------------------
    torchvision.__version__.split                                   : 2
    torchvision.ops.boxes.box_area                                  : 2
    torchvision.datasets.CocoDetection                              : 2
    torchvision.transforms.RandomCrop.get_params                    : 2
    torchvision._is_tracing                                         : 1
    torchvision.ops.misc._output_size                               : 1
    torchvision.ops._new_empty_tensor                               : 1
    torchvision.ops.misc.interpolate                                : 1
    torchvision.transforms.functional.crop                          : 1
    torchvision.transforms.functional.hflip                         : 1
    torchvision.transforms.functional.resize                        : 1
    torchvision.transforms.functional.pad                           : 1
    torchvision.transforms.functional.to_tensor                     : 1
    torchvision.transforms.RandomErasing                            : 1
    torchvision.transforms.functional.normalize                     : 1
    torchvision.models._utils.IntermediateLayerGetter               : 1
    torchvision.models                                              : 1
```
