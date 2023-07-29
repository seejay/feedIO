from distutils.core import setup
import sys

sys.path.append('feedio')
import feedIO


setup(name='feedio',
      version='0.0.5',
      author='Chanaka Jayamal',
      author_email='seejay@seejay.net',
      url='http://feedio.org',
      download_url='https://github.com/seejay/feedIO',
      description='feedIO - A News Aggregator that Knows What You Want to Read.',
      long_description=feedio.feedIO.__doc__,
      package_dir={'': 'feedio'},
      py_modules=['feedIO'],
      provides=['feedIO'],
      keywords='feed rss atom aggregator blogs web ',
      license='GNU General Public License v3',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: X11 Applications :: Qt',
                   'Intended Audience :: End Users/Desktop',
                   'Natural Language :: English',
                   'Operating System :: POSIX :: Linux',
                   'Operating System :: Microsoft :: Windows',
                   'Programming Language :: Python :: 2',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Topic :: Text Processing',
                   'Topic :: Internet :: RSS/ATOM',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
                   'Topic :: Multimedia :: Sound/Audio :: Speech',
                  ],
     )

