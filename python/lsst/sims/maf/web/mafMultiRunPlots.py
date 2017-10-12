from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
import lsst.sims.maf.metricBundles as metricBundles
import lsst.sims.maf.plots as plots
import numpy as np


def overplotOneDHistograms(outDirs, metricName, slicerAbrv, dataframe=None, runList=None,
                           labelList=None, metadata=None, opsim=False,
                           logScale=False, normalize=False, zeroPoint=None):

    plotFuncDict = {'ONED': plots.OneDBinnedData(),
                    'OPSI': plots.OpsimHistogram(),
                    'HEAL': plots.HealpixHistogram()}
    ylabelDict = {'ONED': 'Count',
                  'OPSI': 'Number of Fields',
                  'HEAL': 'Area (1000s of square degrees)'}
    ylabel = ylabelDict[slicerAbrv]
    overPlot = plotFuncDict[slicerAbrv]

    if runList:
        runNames = runList
    if dataframe is not None:
        runNames = dataframe.index
    cmap = plt.cm.get_cmap('gist_rainbow_r')
    bundles = {}
    slicers = {}
    maxYvalues = np.ones(len(runNames))
    for i, run in enumerate(runNames):
        if metadata:
            metadatastr = '_' + metadata
        else:
            metadatastr = ''
        if opsim:
            metricFile = 'opsim' + '_' + metricName + metadatastr + '_' + slicerAbrv + '.npz'
        else:
            metricFile = run + '_' + metricName + metadatastr + '_' + slicerAbrv + '.npz'
        bundles[run + '_' + str(i)] = metricBundles.createEmptyMetricBundle()
        bundles[run + '_' + str(i)].read(run + outDirs[i] + metricFile)
        slicers[run + '_' + str(i)] = bundles[run + '_' + str(i)].slicer
        if slicerAbrv == 'ONED':
            maxYvalues[i] = bundles[run + '_' + str(i)].metricValues.compressed().max()
            bins = None
        else:
            if 'binsize' in bundles[run + '_' + str(i)].plotDict.keys():
                bmin = bundles[run + '_' + str(i)].metricValues.compressed().min()
                bmax = bundles[run + '_' + str(i)].metricValues.compressed().max()
                binsize = bundles[run + '_' + str(i)].plotDict['binsize']
                bins = np.arange(bmin.min() - binsize * 2.0,
                                 bmax.max() + binsize * 2.0, binsize)
            else:
                bins = int(2 * (len(bundles[run + '_' + str(i)].metricValues.compressed())**(1 / 3)))
            hist, edges = np.histogram(bundles[run + '_' + str(i)].metricValues.compressed(),
                                       bins=bins)
            maxYvalues[i] = np.max(hist)
    for k, runPlot in enumerate(runNames):
        runPlot = runPlot + '_' + str(k)
        if labelList:
            label = labelList[k]
        else:
            label = runPlot.strip('_' + str(k))

        if metadata:
            if slicerAbrv == 'ONED':
                xlabel_base = bundles[runPlot].slicer.sliceColName
                title_base = bundles[runPlot].metric.name
                title = title_base + ' (' + metadata + ')'
            if (slicerAbrv == 'OPSI' or slicerAbrv == 'HEAL'):
                xlabel_base = bundles[runPlot].metric.name
                title = ''
                # title_base = bundles[runPlot].displayDict['caption']
            xlabel = xlabel_base + ' (' + metadata + ')'
        else:
            xlabel = bundles[runPlot].slicer.sliceColName
            title = bundles[runPlot].metric.name

        if normalize is False:
            if zeroPoint:
                metricValues = bundles[runPlot].metricValues - zeroPoint
            else:
                metricValues = bundles[runPlot].metricValues
            yMax = np.max(maxYvalues)
        else:
            metricValues = ((bundles[runPlot].metricValues) /
                            (bundles[runPlot].metricValues.compressed().max()))
            yMax = 1.1
            ylabel = 'Normalized Count'
        overPlot(metricValues, slicer=slicers[runPlot],
                 userPlotDict={'color': cmap(k / len(runNames)),
                               'label': label,
                               'linewidth': 3,
                               'ylabel': ylabel,
                               'xlabel': xlabel,
                               'title': title,
                               'yMax': yMax,
                               'logScale': logScale,
                               'bins': bins},
                 fignum=1)

    return overPlot


def subplotSkyMaps(outDirs, metricName, nrows, ncols, slicerAbrv,
                   dataframe=None, runList=None,
                   metadata=None, opsim=False, titleList=None,
                   labelList=None, figsize=None,
                   colorbarRun=None, Lambert=False):
    if runList:
        runNames = runList
    if dataframe is not None:
        runNames = dataframe.index

    plotFuncDict = {'OPSI': plots.BaseSkyMap(),
                    'HEAL': plots.HealpixSkyMap()}
    if Lambert is False:
        subPlots = plotFuncDict[slicerAbrv]
    else:
        subPlots = plots.LambertSkyMap()
    bundles = {}
    userPlotDict = {}
    userPlotDict['figsize'] = figsize

    if ((slicerAbrv == 'HEAL') & ('Alt_Az' in metricName) & (Lambert is False)):
        userPlotDict['rot'] = (0, 90, 0)
    else:
        userPlotDict['rot'] = None
    for i, run in enumerate(runNames):
        if metadata:
            metadatastr = '_' + metadata
        else:
            metadatastr = ''
        if opsim:
            metricFile = 'opsim' + '_' + metricName + metadatastr + '_' + slicerAbrv + '.npz'
        else:
            metricFile = run + '_' + metricName + metadatastr + '_' + slicerAbrv + '.npz'
        bundles[run + '_' + str(i)] = metricBundles.createEmptyMetricBundle()
        bundles[run + '_' + str(i)].read(run + outDirs[i] + metricFile)
    fig = plt.figure(1, figsize=userPlotDict['figsize'])
    if colorbarRun:
        userPlotDict['colorMin'] = bundles[run + '_' + str(i)].metricValues.compressed().min()
        userPlotDict['colorMax'] = bundles[run + '_' + str(i)].metricValues.compressed().max()
    for k, runPlot in enumerate(runNames):
        runPlot = runPlot + '_' + str(k)
        userPlotDict['subplot'] = int(str(nrows) + str(ncols) + str(k + 1))
        if metadata:
            userPlotDict['xlabel'] = bundles[runPlot].metric.name + ' (' + metadata + ')'
        else:
            userPlotDict['xlabel'] = bundles[runPlot].metric.name
        if titleList:
            userPlotDict['title'] = titleList[k]
        else:
            userPlotDict['title'] = runPlot.strip('_' + str(k))

        subPlots(bundles[runPlot].metricValues, slicer=bundles[runPlot].slicer,
                 userPlotDict=userPlotDict, fignum=1)

    plt.suptitle(bundles[runPlot].displayDict['caption'])
