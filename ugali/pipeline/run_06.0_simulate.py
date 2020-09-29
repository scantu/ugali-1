        logger.info("Running 'sensitivity'...")

    if 'merge' in self.opts.run:
        logger.info("Running 'merge'...")

        filenames=join(outdir,self.config['output']['simfile']).split('_%')[0]+'_*'
        infiles=sorted(glob.glob(filenames))

        f = fitsio.read(infiles[0])
        table = np.empty(0,dtype=data.dtype)
        for filename in infiles:
            logger.debug("Reading %s..."%filename)
            d = fitsio.read(filename)
            t = d[~np.isnan(d['ts'])]
            table = recfuncs.stack_arrays([table,t],usemask=False,asrecarray=True)

        logger.info("Found %i simulations."%len(table))
        outfile = join(outdir,"merged_sims.fits")
        logger.info("Writing %s..."%outfile)
        fitsio.write(outfile,table,clobber=True)
        
    if 'plot' in self.opts.run:
        logger.info("Running 'plot'...")
        import ugali.utils.plotting
        import pylab as plt

        plotdir = mkdir(self.config['output']['plotdir'])

        data = fitsio.read(join(outdir,"merged_sims.fits"))
        data = data[~np.isnan(data['ts'])]
        
        bigfig,bigax = plt.subplots()
        
        for dist in np.unique(data['fit_distance']):
            logger.info('  Plotting distance: %s'%dist)
            ts = data['ts'][data['fit_distance'] == dist]
            ugali.utils.plotting.drawChernoff(bigax,ts,bands='none',color='gray')
            
            fig,ax = plt.subplots(1,2,figsize=(10,5))
            ugali.utils.plotting.drawChernoff(ax[0],ts,bands='none',pdf=True)
            ugali.utils.plotting.drawChernoff(ax[1],ts)
            fig.suptitle(r'Chernoff ($\mu = %g$)'%dist)
            ax[0].annotate(r"$N=%i$"%len(ts), xy=(0.15,0.85), xycoords='axes fraction', 
                           bbox={'boxstyle':"round",'fc':'1'})
            basename = 'chernoff_u%g.png'%dist
            outfile = os.path.join(plotdir,basename)
            plt.savefig(outfile)
        bigfig.suptitle('Chernoff!')
        basename = 'chernoff_all.png'
        outfile = os.path.join(plotdir,basename)
        plt.savefig(outfile)

        #idx=np.random.randint(len(data['ts'])-1,size=400)
        #idx=slice(400)
        #ugali.utils.plotting.plotChernoff(data['ts'][idx])
        #ugali.utils.plotting.plotChernoff(data['fit_ts'])
        plt.ion()
        """
        try:
            fig = plt.figure()
            x = range(len(data))
            y = data['fit_mass']/data['stellar_mass']
            yclip,lo,hi = scipy.stats.sigmaclip(y)
            yerr = data['fit_mass_err']/data['stellar_mass']
             
            plt.errorbar(x,y,yerr=yerr,fmt='o',c='k')
            plt.axhline(1,ls='--',c='gray',lw=2)
            plt.axhline(np.mean(yclip),ls='--',c='r',lw=2)
            plt.ylim(lo,hi)
            plt.ylabel("Best-Fit Mass Residual")
            plt.xlabel("Simulation Number")
        except:
            pass
        """

Pipeline.run = run
pipeline = Pipeline(__doc__,components)
pipeline.parser.add_argument('-n','--num',default=None,type=int)
pipeline.parse_args()
pipeline.execute()

import pylab as plt
