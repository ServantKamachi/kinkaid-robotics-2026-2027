using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
public static class BuildPlayground {
 public static void Build(){
  FieldInventory.ValidateContract();FieldScenario.Validate(Application.streamingAssetsPath);Debug.Log("FIELD_INVENTORY_CONTRACT_PASS");
  System.IO.Directory.CreateDirectory("Assets/Resources"); if(AssetDatabase.LoadAssetAtPath<Material>("Assets/Resources/Surface.mat")==null)AssetDatabase.CreateAsset(new Material(Shader.Find("Standard")),"Assets/Resources/Surface.mat");
  PlayerSettings.companyName="169C Robotics";PlayerSettings.productName="Override Playground";PlayerSettings.bundleVersion="0.2.0-dev";PlayerSettings.SetScriptingBackend(UnityEditor.Build.NamedBuildTarget.Standalone,ScriptingImplementation.Mono2x);
  PlayerSettings.SetArchitecture(UnityEditor.Build.NamedBuildTarget.Standalone,1);
  PlayerSettings.defaultScreenWidth=1280;PlayerSettings.defaultScreenHeight=820;PlayerSettings.fullScreenMode=FullScreenMode.Windowed;PlayerSettings.resizableWindow=true;PlayerSettings.runInBackground=true;
  PlayerSettings.colorSpace=ColorSpace.Linear;
  foreach(string path in AssetDatabase.GetAllAssetPaths()){if(!path.EndsWith(".dylib"))continue;var p=AssetImporter.GetAtPath(path) as PluginImporter;if(p!=null){p.SetCompatibleWithAnyPlatform(false);p.SetCompatibleWithEditor(true);p.SetEditorData("OS","OSX");p.SetEditorData("CPU","ARM64");p.SetCompatibleWithPlatform(BuildTarget.StandaloneOSX,true);p.SetPlatformData(BuildTarget.StandaloneOSX,"CPU","ARM64");p.SaveAndReimport();}}
  var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);new GameObject("Override Playground").AddComponent<Playground>();EditorSceneManager.SaveScene(scene,"Assets/Playground.unity");
  var report=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{"Assets/Playground.unity"},locationPathName=System.Environment.GetEnvironmentVariable("OVERRIDE_BUILD_OUTPUT") ?? "../Builds/Candidates/Override Playground.app",target=BuildTarget.StandaloneOSX,options=BuildOptions.None});
  if(report.summary.result!=BuildResult.Succeeded)throw new System.Exception("Build failed: "+report.summary.result);Debug.Log("PLAYGROUND_BUILD_SUCCESS "+report.summary.totalSize);
 }
}
