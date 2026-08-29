"""Haizi Poetry Atlas — analysis pipeline.

A small, dependency-light pipeline that turns a local poetry corpus into
static JSON consumed by the web frontend. The stages are intentionally
separate so each one can be understood, rerun, and tested on its own:

    extract  ->  clean  ->  tokenize  ->  segmentation
                                        ->  imagery
                                        ->  cooccurrence
                                        ->  timeline
                                        ->  export
"""
