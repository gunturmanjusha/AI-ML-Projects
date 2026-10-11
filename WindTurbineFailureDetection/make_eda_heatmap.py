import pandas as pd,matplotlib.pyplot as plt,seaborn as sns
d=pd.read_csv('wind_turbine_detection.csv')
c=['failure','drivetrain_vibration_rms_mmps','tower_vibration_mmps','gearbox_bearing_temp_C','generator_bearing_temp_C','gearbox_oil_temp_C','oil_particle_count','oil_pressure_bar','vib_fft_gearmesh','vib_fft_bearing_bpfi','power_output_kW','ambient_temp_C']
plt.figure(figsize=(11,8));sns.heatmap(d[c].corr(),annot=True,fmt='.2f',cmap='RdBu_r',center=0,vmin=-1,vmax=1,square=True,cbar_kws={'shrink':.75});plt.title('Multivariate correlation of drivetrain condition signals');plt.tight_layout();plt.savefig('outputs/charts/eda_multivariate_correlation.png',dpi=260);print(d[c].corr()['failure'].sort_values())

