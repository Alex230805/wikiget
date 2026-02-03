#!/usr/bin/env python3
# coding=utf-8

import sys;
import requests;
import json;
import os;
import time;

global debug;
global lang;
global limit;
global destination;
global lang_pool;
global argument;
global pages;
global custom_lang;
global strip_suffix;
global strip_prefix;


debug:bool = False;
lang:str ="en";
limit:int = 0;
destination:str ="./"
lang_pool:set = { 
    "en",
    "it"
};
argument = "";
pages:[] = [];
custom_lang:bool = False;
strip_suffix = False;
strip_prefix = False;

def help():
    print("""Wikiget is a fetcher of html pages which is based on the standard API provided by Wikipedia.org. 
By providing a file that contain a list of URLs, Wikiget will perform a sequence of API calls to 
the api.php endpoint of wikipedia to require the desired page and then writing it down into a 
local html page. 
By using the listed argument you can change how the program behave.
    """);
    print("wikiget [param {arg}] list_of_argument.txt\n");
    print(" -h:\n\tprint helper.");
    print(" -l [lang]:\n\tset repo language. You can currently set:");
    print("\t- en: get page from english repo.");
    print("\t- it: get page from italian repo.");
    print("\tBy default the language is enstablished by the URL of each page.");

    print(" -d [path]:\n\tset destination for each page. By default pages will be placed in the same folder where wikiget is executed.");
    print(" -n [max]:\n\tset the number of pages to download. By default all URLs will be fetched");
    print(" --debug:\n\tenable log status from the execution.");
    print(" --strip-suffix:\n\tsave pages without adding the name as a suffix.");
    print(" --strip-prefix:\n\tsave pages without adding the page number prefix.");
    print(" [argument]:\n\ta file with inside a list of page links from whick wikiget will fetch information from the wikipedia api.");
    print("\nExample of a possible usage:\n");
    print("'wikiget -d ./pages -l it -n 10 list'");
    print("'wikiget -d ./pages note.md'");
    return;

def arg_error(cmd:str, message: str):
    print(f"Not a valid argument for '{cmd}' parameter: {message}");
    exit(1);

def write_file(name: str, content: str):
    path = os.path.join(destination,name);
    try:
        fp = open(path, "w");
        fp.write(content);
        fp.close();
    except Exception as ex:
        print(f"Unable to write down file '{path}' due to: {ex}");
        exit(1);
    return;

def read_arg_list(name: str):
    if debug: print(f"[STARTING UP]: Reading argument file from {name}");
    if not len(name) > 0:
        print("Argument file has not been specified");
        exit(1);
    try:
        fp = open(name);
        for line in fp:
            name = line.split("/");
            local_lang = list(name[2].split("."))[0];
            if custom_lang: local_lang = lang;
            page = {
                "name": str(name[len(name)-1]).strip('\n'),
                "lang": local_lang
            };
            pages.append(page);
    except Exception as err:
        print(f"Unable to open argument file '{name}' due to: {err}");
    return;

def wiki_call(page_name: str): 
    api_endpoint: str = 'https://'+page_name["lang"]+'.wikipedia.org/w/api.php';
    api_msg:str = '?action=parse&page=' + page_name["name"] + '&prop=text&formatversion=2&format=json';
    path = api_endpoint + api_msg;
    if debug: print(f"[WIKI CALL]: fetching information from {path}");
    source: object;
    page_dump:str = "";
    try:
        message = f"Fetching {page_name["name"]}".ljust(64);
        print(f"{message}{time.asctime():>}");
        source = requests.get(path, headers={'user-agent': 'fetcher'});
        json_dump = json.loads(source.text);
        page_dump = json_dump['parse']['text'];
    except Exception as ex:
        print(f"Unable to fetch information ({page_name}) from the remote server due to: {ex}");
        exit(1);
    print("Done!");
    return page_dump;

i:int = 0;
argv = sys.argv;
stop:bool = False;
while i < len(argv) and not stop:
    if argv[i] == "-h":
        help();
        exit(1);
    elif argv[i] == "-d":
        if i+1 < len(argv):
            destination = argv[i+1];
            i+=1;
        else:
            arg_error("-d", "missing path for the destination file");
    elif argv[i] == "-n":
        if i+1 < len(argv):
            try:
                limit = int(argv[i+1]);
                i+=1;
            except ValueError as err:
                arg_error("-n", f"not a valid number -> {err}");
        else:
            arg_error("-n", "missing number for the max page option");
    elif argv[i] == "-l":
        if i+1 < len(argv):
            if argv[i+1] not in lang_pool:
                arg_error("-l", f"not a valid language -> {argv[i+1]}");
            else:
                lang = argv[i+1];
                custom_lang = True;
                i+=1;
        else:
            arg_error("-l", "missing language specification");
    elif argv[i] == "--debug":
        debug = True;
    elif argv[i] == "--strip-suffix":
        strip_suffix = True;
    elif argv[i] == "--strip-prefix":
        strip_prefix = True;
    else:
        if len(argv) >= 2:
            if i > 0:
                argument = argv[i];
                stop = True;
        else:
            help();
            exit(1);
    i+=1;


if strip_suffix and strip_prefix:
    print("Cannot have 'strip_prefix' with 'strip_suffix' enabled at the same time, it will result in an invalid name");
    exit(1);

read_arg_list(argument);

if limit == 0:
    limit = len(pages);

if debug:
    print("wikiget config set (from the command line arguments):");
    print(f"lang: {lang}");
    print(f"page limit: {limit}");
    print(f"destination: {destination}");
    print(f"argument list: {argument}");
    print(f"strip_suffix: {strip_suffix}");
    print(f"strip_prefix: {strip_prefix}");


for i, page in enumerate(pages):
    if i < limit:
        raw_text:str = wiki_call(page);
        dest_name: str = "";
        if not strip_prefix:
            dest_name += "page_"+str(i)+"_";
        if not strip_suffix:
            dest_name += page["name"].lower();
        dest_name += ".html";
        write_file(dest_name, raw_text);
    else:
        break;

print(f"Closing. Total required time: {time.thread_time():5.3f} seconds");
