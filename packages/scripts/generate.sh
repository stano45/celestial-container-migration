printf "Generating aggregate plots...\n"
python src/plot_duration_vs_instance_size.py ../../data/migration-0.csv ../../data/migration-100.csv ../../data/migration-500.csv ../../data/migration-1000.csv ../../data/migration-1500.csv ../../data/migration-2000.csv
python src/plot_average_migration_components.py ../../data/migration-0.csv ../../data/migration-100.csv ../../data/migration-500.csv ../../data/migration-1000.csv ../../data/migration-1500.csv ../../data/migration-2000.csv
python src/plot_average_migration.py ../../data/migration-0.csv ../../data/migration-100.csv ../../data/migration-500.csv ../../data/migration-1000.csv ../../data/migration-1500.csv ../../data/migration-2000.csv 
python src/plot_downtime.py
./generate_plots_for_experiment.sh ../../data/migration-0.csv ../../data/client-0.csv "empty instance" 
./generate_plots_for_experiment.sh ../../data/migration-100.csv ../../data/client-100.csv "100 MB instance"
./generate_plots_for_experiment.sh ../../data/migration-500.csv ../../data/client-500.csv "500 MB instance"
./generate_plots_for_experiment.sh ../../data/migration-1000.csv ../../data/client-1000.csv "1000 MB instance"
./generate_plots_for_experiment.sh ../../data/migration-1500.csv ../../data/client-1500.csv "1500 MB instance"
./generate_plots_for_experiment.sh ../../data/migration-2000.csv ../../data/client-2000.csv "2000 MB instance"
# ./generate_plots_for_experiment.sh ../../data/migration-5000.csv ../../data/client-5000-clipped.csv "5000 MB instance"
