from pathlib import Path
import pandas as pd

APP_DIR = Path("data/processed/app")
APP_DIR.mkdir(parents=True, exist_ok=True)

def build_model_results() -> pd.DataFrame:
    rows = [
        ["weekly","V0_dummy_mean","dummy","produccion_semanal_proxy_t",32.827842,28.887284,52.267359,-0.005957,0.0,54.101825,41.430388,50.708064,-0.097971,0.0,0,"benchmark mínimo"],
        ["weekly","V1_baseline_ridge","ridge","produccion_semanal_proxy_t",17.537376,12.641844,16.668015,0.712906,0.8781665,44.225584,32.539383,32.406730,0.266407,0.9102976,0,"baseline interpretable"],
        ["weekly","V2_clima_crudo_ridge","ridge","produccion_semanal_proxy_t",18.392441,13.374363,17.962554,0.684228,0.8729403,46.651656,35.911898,37.966539,0.183603,0.9112922,0,"ridge con clima crudo"],
        ["weekly","V3_clima_derivado_ridge","ridge","produccion_semanal_proxy_t",18.728962,13.855422,18.345589,0.672567,0.8800123,47.583890,36.347945,37.900511,0.150649,0.9035232,0,"ridge con clima derivado"],
        ["weekly","V4_indice_base_ridge","ridge","produccion_semanal_proxy_t",17.214336,12.380985,16.373496,0.723385,0.8806039,43.575609,31.664100,31.134631,0.287715,0.9804890,0,"ridge con índice agregado"],
        ["weekly","V5_clima_crudo_rf","random_forest","produccion_semanal_proxy_t",15.397304,11.707438,18.710357,0.778699,0.8927368,36.010520,22.345469,20.564865,0.511001,0.8774270,0,"modelo weekly relevante"],
        ["weekly","V6_clima_derivado_rf","random_forest","produccion_semanal_proxy_t",16.548826,12.727973,20.205473,0.744360,0.8680843,36.069071,22.459488,21.560448,0.511981,0.8626105,0,"rf con clima derivado"],
        ["weekly","V7_clima_mas_economicas_rf","random_forest","produccion_semanal_proxy_t",15.321890,11.567698,18.244034,0.780861,0.899377,30.599104,19.523131,19.084154,0.648776,0.940189,1,"capa operativa semanal"],
        ["weekly","V8_clima_derivado_xgb","xgboost","produccion_semanal_proxy_t",15.952924,11.738012,18.239108,0.762439,0.8859107,36.555220,23.281675,21.873696,0.498737,0.8881088,0,"alternativa boosting weekly"],
        ["monthly","M0_dummy","dummy","produccion_mensual_proxy_t",142.549263,126.065166,52.570857,-0.006202,None,238.107355,181.420834,50.775558,-0.101330,None,0,"benchmark mínimo"],
        ["monthly","M1_baseline_ridge","ridge","produccion_mensual_proxy_t",78.892816,56.743334,17.702441,0.691802,0.866814,197.843496,145.573700,33.175808,0.239647,0.906704,0,"baseline interpretable"],
        ["monthly","M2_clima_ridge","ridge","produccion_mensual_proxy_t",79.485377,56.139117,17.930598,0.687155,0.876057,202.651383,153.081724,36.265997,0.202242,0.903261,0,"ridge con clima"],
        ["monthly","M3_clima_econ_ridge","ridge","produccion_mensual_proxy_t",230.321159,195.049550,81.724390,-1.626776,0.531577,315.690923,204.126154,65.817494,-0.935958,0.294977,0,"ridge clima+economía débil"],
        ["monthly","M4_clima_rf","random_forest","produccion_mensual_proxy_t",72.813176,54.258213,20.544667,0.737472,0.863496,161.853241,99.122637,21.435547,0.491121,0.840240,0,"rf con clima"],
        ["monthly","M5_clima_econ_rf","random_forest","produccion_mensual_proxy_t",66.338504,49.416095,18.316781,0.782085,0.896468,149.602184,92.428560,20.402728,0.565242,0.908368,1,"referencia climática mensual"],
        ["monthly","M6_clima_econ_struct_rf","random_forest","produccion_mensual_proxy_t",62.916842,47.368175,17.654082,0.803985,0.902436,144.717542,87.722928,19.817314,0.593179,0.883121,1,"capa operativa mensual"],
        ["monthly","M7_clima_econ_xgb","xgboost","produccion_mensual_proxy_t",62.965575,46.074339,16.752319,0.803675,0.923942,150.300998,94.254008,20.326027,0.561171,0.929572,0,"alternativa boosting mensual"],
        ["annual","A0_dummy","dummy","rendimiento_departamental_t_ha",0.200360,0.163200,19.429666,-0.041511,None,0.298885,0.254000,18.022514,-2.599774,None,0,"benchmark mínimo annual"],
        ["annual","A1_baseline_ridge","ridge","rendimiento_departamental_t_ha",0.120078,0.089131,8.042474,0.625918,0.840867,0.426870,0.412754,31.613625,-6.342764,0.788247,1,"contraste metodológico annual"],
        ["annual","A2_clima_ridge","ridge","rendimiento_departamental_t_ha",0.152888,0.145005,15.662424,0.393554,0.738113,0.268896,0.235498,17.682022,-1.913656,0.670529,0,"clima annual no supera baseline"],
        ["annual","A3_clima_econ_ridge","ridge","rendimiento_departamental_t_ha",0.157939,0.150905,16.331060,0.352828,0.739879,0.252663,0.216858,16.249443,-1.572479,0.671771,0,"clima+economía annual no supera baseline"],
        ["annual","A0_dummy","dummy","produccion_anual_departamental_t",1514.169989,1467.632600,48.079300,-0.007930,None,2502.155224,2046.198600,43.934109,-0.136335,None,0,"benchmark mínimo annual"],
        ["annual","A1_baseline_ridge","ridge","produccion_anual_departamental_t",643.781529,412.389795,10.040663,0.817796,0.943882,2030.094752,1744.088304,35.868985,0.251985,0.998905,1,"contraste metodológico annual"],
        ["annual","A2_clima_ridge","ridge","produccion_anual_departamental_t",1670.952811,1533.484610,46.868226,-0.227466,0.901447,3495.362701,3198.076290,73.548390,-1.217493,0.823629,0,"clima annual agregado insuficiente"],
        ["annual","A3_clima_econ_ridge","ridge","produccion_anual_departamental_t",1388.694195,1213.422224,36.270118,0.152199,0.898327,2992.643019,2633.441604,57.625414,-0.625502,0.818509,0,"clima+economía annual peor que baseline"],
    ]
    return pd.DataFrame(rows, columns=[
        "frecuencia","modelo","familia_modelo","target",
        "val_RMSE","val_MAE","val_MAPE_pct","val_R2","val_Corr",
        "test_RMSE","test_MAE","test_MAPE_pct","test_R2","test_Corr",
        "seleccionado","rol_modelo"
    ])

def build_traceability() -> pd.DataFrame:
    rows = [
        [1, "¿Cómo se comportan el clima, la producción proxy y el contexto económico por departamento y período?", "monthly", "capa descriptiva", "No aplica", "Diagnóstico territorial claro", "lectura descriptiva, no causal"],
        [1, "¿Qué departamentos muestran mayor exposición o mayor variabilidad?", "monthly", "capa descriptiva", "No aplica", "Comparación territorial", "proxy productiva y agregación mensual"],
        [2, "¿Qué modelo funciona mejor para cada propósito del artefacto?", "weekly", "V7_clima_mas_economicas_rf", "test_RMSE / test_R2 / test_Corr", "Mejor capa operativa semanal", "alta influencia territorial"],
        [2, "¿Qué modelo sostiene mejor el análisis mensual del artefacto?", "monthly", "M6_clima_econ_struct_rf", "val_RMSE / val_R2 / test_R2", "Mejor capa operativa mensual", "dominancia estructural"],
        [2, "¿Qué modelo conserva mejor la lógica climática del seguro?", "monthly", "M5_clima_econ_rf", "test_Corr / test_R2", "Referencia climática mensual", "ajuste levemente inferior a M6"],
        [2, "¿Qué capa sirve como contraste metodológico conservador?", "annual", "A1_baseline_ridge", "val_RMSE / val_R2 / test_Corr", "Transparencia metodológica", "muestra pequeña y señal climática annual débil"],
        [3, "¿Qué zonas presentan mayor riesgo y qué señales justifican monitoreo?", "monthly + weekly", "M6/M5 + V7", "Métricas monthly + señal weekly", "Soporte técnico al seguro", "weekly no es inferencia causal fuerte"],
        [3, "¿Cómo se traduce el análisis en una herramienta útil para el seguro indexado?", "monthly", "M6/M5", "Val/test métricas monthly", "Lectura operativa para monitoreo y revisión técnica", "la app no reemplaza un cálculo actuarial completo"],
    ]
    return pd.DataFrame(rows, columns=[
        "pagina","pregunta_analitica","frecuencia","modelo_o_capa",
        "metrica_clave","resultado_esperado","limitacion_clave"
    ])

def main() -> None:
    model_results = build_model_results()
    traceability = build_traceability()
    model_results.to_csv(APP_DIR / "model_results.csv", index=False, encoding="utf-8")
    traceability.to_csv(APP_DIR / "model_traceability.csv", index=False, encoding="utf-8")
    print("[OK] model_results.csv", model_results.shape)
    print("[OK] model_traceability.csv", traceability.shape)

if __name__ == "__main__":
    main()
