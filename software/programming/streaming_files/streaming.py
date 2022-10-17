
import chunk
import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)


# NO ADDITIONAL IMPORTS!


# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


# functions for lab 6

redirect = set([301,302,307])

def is_manifest(url):
    '''
    >>> url  = 'http://mit.edu/6.009/www/lab6_examples/yellowsub.txt.parts'
    >>> is_manifest(url)
    True
    '''
    w = http_response(url)
    
    b = '.parts' == url[-6:]
    
    b2 = w.getheader('content-type')
    
    if b2: b2 = b2 == 'text/parts-manifest'
    
    
    return b or b2   
    
def successful(r, chunk_size, is_cache=False):
    
    if r.status in redirect:
        yield successful(http_response(r.getheader('location')), chunk_size, is_cache)
        
    if is_cache:
        yield r.read()

    else:
    
        c = r.read(chunk_size)
        while c != b'':
            yield c
            c = r.read(chunk_size)

def download_file(url, chunk_size=8192, is_cache=False, cache=None):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """
    
    # handling errors
    try:
        r = http_response(url)
    except ConnectionError:
        raise HTTPRuntimeError 
          
    if r.status == 404: raise HTTPFileNotFoundError
    
    elif r.status == 500: raise HTTPRuntimeError
                    
    # if redirect
    elif r.status in redirect:
        yield from download_file(r.getheader('location'), chunk_size, is_cache, cache)
    
    # if manifest
    elif is_manifest(url): 
        if cache is None:
            cache = {}
              
        c = 'TEST'                 
                
        # while there is something
        while c != b'': 
            
            c = r.readline()
                
            is_cache = False
            
            if c == b'--\n':
            # get new line, url 
                c = r.readline()
            
            tmp_section = []      
            
            # get all the URL in that section
            while c != b'--\n' and c != b'': 
                
                try:
                    URL = c.decode('utf-8').strip()   
                except UnicodeDecodeError:
                    URL = c.decode('utf-16').strip()
                    
                if URL == '(*)':
                    is_cache = True
                else:
                    tmp_section.append(URL)
                
                c = r.readline()
                    
                
            if is_cache: 
                found = False
                for URL in tmp_section:
            
                    # if any URL is already in cache
                    if cache.get(URL, False):
                        found = True
                        yield cache[URL]
                        break
        
                # if no URL is in cache
                if not found:
                    
                    # search a URL that works
                    for URL in tmp_section:
                        
                        try:
                            file = download_file(URL, chunk_size, is_cache=True, cache=cache)
                            cache[URL] = b''
                            for line in file:
                                cache[URL]+= line
                                
                            yield cache[URL]
                            break
                        
                        # if it failed, go to next iteration
                        except:
                            continue  
            else:
                for URL in tmp_section:
                    try:
                        yield from download_file(URL, chunk_size, is_cache=False, cache=cache)
                        break
                    # if it failed, go to next iteration
                    except:
                        continue
             
    # if successful 
    elif r.status == 200:    
        if is_cache:
            yield from successful(r, chunk_size, is_cache=True)
        else:
            yield from successful(r, chunk_size)

def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """
    s = next(stream, None)
    remaining_leng = 0
    tmp_len = b''
    data = b''
    
    while s is not None:
        #-------finishing remaining_leng of data-----#
        
        # checking if there is something left
        if remaining_leng != 0: 
            
            # if remaining_leng is greater 
            # or equal to than lenght of chunck_size
            if remaining_leng > len(s):
                data += s[:]
                remaining_leng -= len(s)
                
                s = next(stream, None)
                continue
            
            # if remaining_leng is less than
            # or equal to chunk_size
            else:
                
                data += s[:remaining_leng]
                yield data
                
                # update var
                s = s[remaining_leng:]

                
        #--------getting remaining_leng-------#
        data = b''
        remaining_leng = 0
        
        # if size of remaining chunk is less than 4 
        # or there is something in tmp_len
        if len(s) < 4 or tmp_len != b'':
                
            # while tmp_size is not 4 bytes and
            # s has not been exhausted
            while len(tmp_len) < 4 and s != b'':
                tmp_len += s[0:1]
                s = s[1:]
            
            # if successfull in getting tmp_len
            if len(tmp_len) == 4:
                remaining_leng = int.from_bytes(tmp_len, byteorder='big')
                tmp_len = b'' 
                
            # if s is empty, go to next chunk  
            elif s == b'':
                s = next(stream, None)
                continue
        
        # if tmp_len is empty and len(s) >=4 
        else:
            remaining_leng = int.from_bytes(s[:4], byteorder='big')
            s = s[4:]
            
        #--------getting data-----------#
        '''
        Assumes len(s) >= 0 and data = b'' 
        '''
        
        # while s has not been exhausted
        while s != b'':
            
            # if entire bytearray is in s
            if len(s) >= remaining_leng:
                data = s[:remaining_leng]
                s = s[remaining_leng:]
                
                # yield data and reset vars
                yield data
                data = b''
                
                # if able to get another chunk
                if len(s) >= 4:
                    remaining_leng = int.from_bytes(s[:4], byteorder='big')
                    s = s[4:]
                
                # get rest of leng
                else:
                    remaining_leng = 0
                    tmp_len = s[:]
                    s = b''
            
            # not able to get entire bytearray
            else:
                # data is remaining
                data = s[:]
                remaining_leng -= len(s)
                
                # exhausted s
                s = b''
                
        s = next(stream, None)
        
        
# URL = sys.argv[1]
# FILENAME = sys.argv[2]

# with open(FILENAME, 'wb') as f:
#     for ix, data in enumerate(files_from_sequence(download_file(URL))):
#         if ix == 52:
#             f.write(data)
#             break
#     f.close()        

if __name__ == "__main__":
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    
    