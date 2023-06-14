# (C) Copyright 2023 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

import sys
from urllib.parse import urlparse, urlunparse

import hydra
import zarr
from omegaconf import DictConfig, OmegaConf


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    print(sys.argv)
    print(OmegaConf.to_yaml(cfg))


def open_directory(uri):
    p = urlparse(uri)
    return zarr.storage.DirectoryStore(p.path)


def open_http(uri):
    import s3fs

    p = urlparse(uri)
    print(uri)

    endpoint = urlunparse((p.scheme, p.netloc, "", "", "", ""))
    path = urlunparse(("", "", p.path, p.params, p.query, p.fragment))
    print(endpoint)
    print(path)

    fs = s3fs.S3FileSystem(
        anon=True,
        client_kwargs={"endpoint_url": endpoint},
    )

    return s3fs.S3Map(
        root=path,
        s3=fs,
        check=False,
    )


def zarr_open(uri, cache=None):
    p = urlparse(uri)

    OPENERS = dict(https=open_http, http=open_http, file=open_directory)
    OPENERS[""] = open_directory

    store = OPENERS[p.scheme](uri)
    if cache is not None:
        store = zarr.storage.LRUStoreCache(store, max_size=cache)

    return zarr.open(store, mode="r")


if __name__ == "__main__":
    main()
