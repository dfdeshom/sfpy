try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages
                        
setup(
    name = "sfpy",
    version = "1.0",
    description = "Another Python client for the SuperFeedr XMPP service",
    author = 'didier deshommes',
    author_email = 'dfdeshom@gmail.com',
    packages=find_packages(exclude=['ez_setup']),
    classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
    ],
    url = 'http://bitbucket.org/dfdeshom/sfpy/overview/'
    )
