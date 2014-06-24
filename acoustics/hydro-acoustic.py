#!/usr/bin/env python
import gzip
import obspy
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt
#import obspy.core

st = obspy.core.read(gzip.open('bdsAutodrm-1ZoNHK.gz', 'r'), verify_chksum=False)
print `st`
for tr in st:
    msg = "%s %s %f %f" % (tr.stats.station, str(tr.stats.starttime),
                           tr.data.mean(), tr.data.std())
    print msg

dt = st[0].stats.starttime
pdf_pages = matplotlib.backends.backend_pdf.PdfPages('multipage_pdf.pdf')
for t in xrange(0, 30):
    # A4 landscape, in inches(!)
    #fig = plt.figure(figsize=(11.69, 8.27))
    # Wide-screen 16:9
    fig = plt.figure(figsize=(8.27*16/9., 8.27))
    st.plot(color='gray', linewidth=0.1, alpha=0.3, number_of_ticks=7, size=(1500,800),
        tick_rotation=5, tick_format='%H:%M:%S', fig=fig,
        starttime=dt + t*60, endtime=dt + (t+1) * 60, outfile=str(t) + '.pdf', show=False)
    pdf_pages.savefig(fig)
    #st.spectrogram(log=True, show=False)
    #pdf.savefig()

pdf_pages.close()
