import pandas as pd
import os


dataset_path = '.local/datasets/RawGazeDataFromPupilCorePupilData/'
output_path = '.local/datasets/PupilCoreV1_all/'

if not os.path.exists(output_path):
    os.makedirs(output_path)
    
all_files = os.listdir(dataset_path)
all_files = [f for f in all_files if f.endswith('.csv')]


for i, file in enumerate(all_files):
    print(i, file)
    df = pd.read_csv(dataset_path + file)


    # Sort the dataframe by 'pupil_timestamp'
    df = df.sort_values(by='pupil_timestamp')

    # Select all rows with method 2d c++
    df_2d = df[df['method'] == '2d c++'].dropna(thresh=len(df) / 2, axis=1)
    df_3d = df[df['method'] == 'pye3d 0.0.7 real-time'].dropna(thresh=len(df) / 2, axis=1)
    
    df_1 = df_2d[df_2d['eye_id'] == 0]
    df_2 = df_2d[df_2d['eye_id'] == 1]
    df_3 = df_3d[df_3d['eye_id'] == 0]
    df_4 = df_3d[df_3d['eye_id'] == 1]

    other_cols = ['world_index', 'confidence', 'method']

    # Merge the dataframes by 'pupil_timestamp' using merge_asof
    df_1 = df_1.drop(columns=other_cols)
    df_2 = df_2.drop(columns=other_cols)
    df_3 = df_3.drop(columns=other_cols)
    df_4 = df_4.drop(columns=other_cols)
    
    df_12 = pd.merge_asof(df_1, df_2, on='pupil_timestamp', suffixes=('_2d_0', '_2d_1'))
    df_34 = pd.merge_asof(df_3, df_4, on='pupil_timestamp', suffixes=('_3d_0', '_3d_1'))
    df_all = pd.merge_asof(df_12, df_34, on='pupil_timestamp')
    
    df_all.drop(columns=['eye_id_2d_0', 'eye_id_2d_1', 'eye_id_3d_0', 'eye_id_3d_1'], inplace=True)

    
    cols = ['pupil_timestamp', 'eye_id_1', 'norm_pos_x_1', 'norm_pos_y_1',
       'diameter_1', 'ellipse_center_x_1', 'ellipse_center_y_1',
       'ellipse_axis_a_1', 'ellipse_axis_b_1', 'ellipse_angle_1', 'eye_id_2',
       'norm_pos_x_2', 'norm_pos_y_2', 'diameter_2', 'ellipse_center_x_2',
       'ellipse_center_y_2', 'ellipse_axis_a_2', 'ellipse_axis_b_2',
       'ellipse_angle_2', 'eye_id_3', 'norm_pos_x_3', 'norm_pos_y_3',
       'diameter_3', 'ellipse_center_x_3', 'ellipse_center_y_3',
       'ellipse_axis_a_3', 'ellipse_axis_b_3', 'ellipse_angle_3',
       'diameter_3d_3', 'model_confidence_3', 'sphere_center_x_3',
       'sphere_center_y_3', 'sphere_center_z_3', 'sphere_radius_3',
       'circle_3d_center_x_3', 'circle_3d_center_y_3', 'circle_3d_center_z_3',
       'circle_3d_normal_x_3', 'circle_3d_normal_y_3', 'circle_3d_normal_z_3',
       'circle_3d_radius_3', 'theta_3', 'phi_3', 'projected_sphere_center_x_3',
       'projected_sphere_center_y_3', 'projected_sphere_axis_a_3',
       'projected_sphere_axis_b_3', 'projected_sphere_angle_3', 'eye_id_4',
       'norm_pos_x_4', 'norm_pos_y_4', 'diameter_4', 'ellipse_center_x_4',
       'ellipse_center_y_4', 'ellipse_axis_a_4', 'ellipse_axis_b_4',
       'ellipse_angle_4', 'diameter_3d_4', 'model_confidence_4',
       'sphere_center_x_4', 'sphere_center_y_4', 'sphere_center_z_4',
       'sphere_radius_4', 'circle_3d_center_x_4', 'circle_3d_center_y_4',
       'circle_3d_center_z_4', 'circle_3d_normal_x_4', 'circle_3d_normal_y_4',
       'circle_3d_normal_z_4', 'circle_3d_radius_4', 'theta_4', 'phi_4',
       'projected_sphere_center_x_4', 'projected_sphere_center_y_4',
       'projected_sphere_axis_a_4', 'projected_sphere_axis_b_4',
       'projected_sphere_angle_4']

    # save the dataframe
    df_all.to_csv(output_path + file, index=False)