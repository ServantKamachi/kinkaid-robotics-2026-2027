using UnityEngine;
using UnityEngine.Rendering;
using System;
using System.IO;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
using Stopwatch=System.Diagnostics.Stopwatch;

public class Playground : MonoBehaviour {
 [DllImport("override")] static extern int pg_engine_version();
 [DllImport("override")] static extern int pg_load(string path,StringBuilder error,int cap);
 [DllImport("override")] static extern void pg_close();
 [DllImport("override")] static extern void pg_reset(int scene);
 [DllImport("override")] static extern void pg_step(int count);
 [DllImport("override")] static extern void pg_command(double f,double t,double l,double j,double r);
 [DllImport("override")] static extern int pg_body(string name);
 [DllImport("override")] static extern void pg_poses([Out] double[] poses);
 [DllImport("override")] static extern void pg_status([Out] double[] status);
 [Serializable] public class Entry {public string file,body;public float[] rgba,position,rotation;}
 [Serializable] public class Manifest {public Entry[] meshes;}
 FieldInventory inventory=new FieldInventory();
 bool stadium,stadiumAtStart,uiCheck;
 Dictionary<string,List<Renderer>> meshGroups=new Dictionary<string,List<Renderer>>();
 List<GameObject> practiceDetails=new List<GameObject>();
 Dictionary<int,Transform> bodies=new Dictionary<int,Transform>();
 Dictionary<string,Transform> bodyTransforms=new Dictionary<string,Transform>();
 bool stadiumPiecesLoaded;
 double[] poses,status=new double[12];Camera cam;Light sun;int robotId,scene=0,view=0;bool paused,help=true,demo;string error="";
 float yaw=20,pitch=55,distance=5.9f,zoomTarget=5.9f;Vector3 focus=new Vector3(0,.10f,-.05f);
 double accumulator;float fps=60,physicsMs,elapsed,metricClock;int stepsTotal;List<float> frames=new List<float>();List<float> costs=new List<float>();
 GUIStyle title,body,small,kicker,button,stat;Texture2D white;Font font;Stopwatch timer=new Stopwatch();float ui=1;int panel=280;string[] sceneNames={"Claw pickup","Loose-piece pile","Stack & release"};
 [Serializable] class SlowFrame {public float elapsedSeconds,frameMs,physicsMs,previousPhysicsMs;public double contacts,previousContacts,simulationSeconds;}
 List<SlowFrame> slowFrames=new List<SlowFrame>();float previousPhysics;double previousContacts;
 bool automated,benchmark,captureBenchmark,startupCheck,firstFrame=true;double maxBacklog;Stopwatch wallClock=new Stopwatch();float autoDuration=65;string evidence;bool screenshotTaken;
 void Awake(){try{Initialize();}catch(Exception ex){error="The playground could not start.\n\n"+ex.Message+"\n\nRestore the complete application folder or rebuild using Tools/build_candidate.py.";Debug.LogError(error);try{pg_close();}catch{}poses=null;}}
 void Initialize(){
  if(pg_engine_version()!=3013000)throw new Exception("Native physics version mismatch; expected MuJoCo 3.13.0.");
  Application.targetFrameRate=60;QualitySettings.vSyncCount=0;QualitySettings.antiAliasing=2;QualitySettings.shadowDistance=8;QualitySettings.shadows=ShadowQuality.All;QualitySettings.shadowResolution=ShadowResolution.High;QualitySettings.shadowCascades=2;
  Application.runInBackground=true;Time.maximumDeltaTime=.10f;
  var args=Environment.GetCommandLineArgs();for(int i=0;i<args.Length;i++){if(args[i]=="--ui-check")uiCheck=true;if(args[i]=="--stadium")stadiumAtStart=true;if(args[i]=="--startup-check"){startupCheck=true;automated=true;demo=false;autoDuration=2;}if(args[i]=="--benchmark"){automated=true;benchmark=true;}if(args[i]=="--view"&&i+1<args.Length)int.TryParse(args[i+1],out view);if(args[i]=="--capture")captureBenchmark=true;if(args[i]=="--scene"&&i+1<args.Length)int.TryParse(args[i+1],out scene);if(args[i]=="--duration"&&i+1<args.Length)float.TryParse(args[i+1],out autoDuration);if(args[i]=="--evidence"&&i+1<args.Length)evidence=args[i+1];}
  if(evidence==null)evidence=Path.Combine(Application.persistentDataPath,"Evidence");Directory.CreateDirectory(evidence);
  var msg=new StringBuilder(4096);int n=pg_load(Path.Combine(Application.streamingAssetsPath,"playground.xml"),msg,4096);if(n==0){error=msg.ToString();return;}poses=new double[n*7];robotId=pg_body("robot");
  LoadMeshes("Robot");LoadMeshes("Field");LoadMeshes("ReusedPieces");LoadMeshes("Stadium");SetPoses();
  cam=new GameObject("Practice camera").AddComponent<Camera>();cam.clearFlags=CameraClearFlags.SolidColor;cam.backgroundColor=new Color(.32f,.32f,.32f);cam.nearClipPlane=.015f;cam.farClipPlane=40;cam.fieldOfView=43;
  sun=new GameObject("Soft key light").AddComponent<Light>();sun.type=LightType.Directional;sun.transform.rotation=Quaternion.Euler(48,-35,0);sun.intensity=1.2f;sun.color=new Color(1,.955f,.88f);sun.shadows=LightShadows.Soft;sun.shadowBias=.025f;sun.shadowNormalBias=.015f;sun.shadowStrength=.65f;
  var fill=new GameObject("Cool fill").AddComponent<Light>();fill.type=LightType.Directional;fill.transform.rotation=Quaternion.Euler(60,145,0);fill.color=new Color(.55f,.73f,1);fill.intensity=.42f;
  RenderSettings.ambientMode=AmbientMode.Trilight;RenderSettings.ambientSkyColor=new Color(.52f,.60f,.68f);RenderSettings.ambientEquatorColor=new Color(.28f,.32f,.37f);RenderSettings.ambientGroundColor=new Color(.14f,.17f,.20f);
  MakeDetails();ResetScene(Mathf.Clamp(scene,0,2));paused=startupCheck;SelectView(Mathf.Clamp(view,0,2));if(uiCheck){for(int cycle=0;cycle<5;cycle++){SetStadium(true);if(!stadium||meshGroups["Stadium"].Exists(r=>!r.enabled)||meshGroups["Robot"].Exists(r=>!r.enabled)||inventory.Count(FieldInventory.Location.Field)!=73)throw new Exception("Stadium visibility check failed");ResetScene(cycle%3);if(stadium||paused||meshGroups["Robot"].Exists(r=>!r.enabled)||meshGroups["Stadium"].Exists(r=>r.enabled))throw new Exception("Practice restore check failed");}Debug.Log("SCENE_SWITCH_CHECK_PASS 5 cycles");}int requestedView=view;SetStadium(stadiumAtStart);SelectView(Mathf.Clamp(requestedView,0,2));if(benchmark&&!startupCheck){paused=false;demo=true;}SetCamera(true);wallClock.Start();Debug.Log("PLAYGROUND_READY native MuJoCo 3.13.0 bodies="+poses.Length/7);
 }
 Material MaterialFor(Color c){var m=new Material(Resources.Load<Material>("Surface"));m.color=c;m.SetFloat("_Glossiness",.25f);m.SetFloat("_Metallic",c.r>.45f&&c.g>.45f?.25f:0);if(c.a<.99f){m.SetFloat("_Mode",3);m.SetInt("_SrcBlend",(int)BlendMode.SrcAlpha);m.SetInt("_DstBlend",(int)BlendMode.OneMinusSrcAlpha);m.SetInt("_ZWrite",0);m.EnableKeyword("_ALPHABLEND_ON");m.renderQueue=3000;}return m;}
 void LoadMeshes(string folder){meshGroups[folder]=new List<Renderer>();var path=Path.Combine(Application.streamingAssetsPath,folder);var manifest=JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(path,"manifest.json")));var cache=new Dictionary<string,Mesh>();var materials=new Dictionary<string,Material>();
 foreach(var entry in manifest.meshes){int id=entry.body=="world"?0:pg_body(entry.body);if(id<0)throw new Exception("Missing physical body: "+entry.body);if(!bodyTransforms.ContainsKey(entry.body))bodyTransforms[entry.body]=new GameObject(entry.body).transform;bodies[id]=bodyTransforms[entry.body];
 if(!cache.TryGetValue(entry.file,out Mesh mesh)){using(var reader=new BinaryReader(File.OpenRead(Path.Combine(path,entry.file)))){int nv=reader.ReadInt32(),ni=reader.ReadInt32();var v=new Vector3[nv];var indices=new int[ni];for(int j=0;j<nv;j++)v[j]=new Vector3(reader.ReadSingle(),reader.ReadSingle(),reader.ReadSingle());for(int j=0;j<ni;j++)indices[j]=reader.ReadInt32();mesh=new Mesh();mesh.indexFormat=IndexFormat.UInt32;mesh.vertices=v;mesh.triangles=indices;if(reader.BaseStream.Length-reader.BaseStream.Position>=nv*12){var normals=new Vector3[nv];for(int j=0;j<nv;j++)normals[j]=new Vector3(reader.ReadSingle(),reader.ReadSingle(),reader.ReadSingle());mesh.normals=normals;}else mesh.RecalculateNormals();mesh.RecalculateBounds();cache.Add(entry.file,mesh);}}
 string color=string.Join(",",entry.rgba);if(!materials.TryGetValue(color,out Material material)){material=MaterialFor(new Color(entry.rgba[0],entry.rgba[1],entry.rgba[2],entry.rgba[3]));material.enableInstancing=true;materials.Add(color,material);}
 var go=new GameObject(entry.file);go.transform.SetParent(bodies[id],false);if(entry.position!=null&&entry.position.Length==3)go.transform.localPosition=new Vector3(entry.position[0],entry.position[1],entry.position[2]);if(entry.rotation!=null&&entry.rotation.Length==4)go.transform.localRotation=new Quaternion(entry.rotation[0],entry.rotation[1],entry.rotation[2],entry.rotation[3]);go.AddComponent<MeshFilter>().sharedMesh=mesh;var renderer=go.AddComponent<MeshRenderer>();renderer.sharedMaterial=material;meshGroups[folder].Add(renderer);if(entry.rgba[3]<.99f)renderer.shadowCastingMode=ShadowCastingMode.Off;}
 }
 void DetailBox(string name,Vector3 p,Vector3 size,Color color){var go=GameObject.CreatePrimitive(PrimitiveType.Cube);go.name=name;practiceDetails.Add(go);Destroy(go.GetComponent<Collider>());go.transform.position=p;go.transform.localScale=size;go.GetComponent<Renderer>().sharedMaterial=MaterialFor(color);}
 void MakeDetails(){
  // Flush, non-colliding markings: contacts are owned exclusively by MuJoCo.
  Color seam=new Color(.21f,.25f,.28f);for(int i=1;i<6;i++){float p=-1.7832f+i*3.5664f/6;DetailBox("Tile seam",new Vector3(p,.0003f,0),new Vector3(.002f,.0005f,3.5664f),seam);DetailBox("Tile seam",new Vector3(0,.0003f,p),new Vector3(3.5664f,.0005f,.002f),seam);}
  for(int s=-1;s<=1;s+=2){DetailBox("Alliance edge",new Vector3(s*1.77f,.003f,0),new Vector3(.021f,.003f,3.55f),s<0?new Color(.65f,.1f,.13f):new Color(.08f,.32f,.7f));}
  for(int i=0;i<3;i++){var g=new GameObject("Target label");practiceDetails.Add(g);var t=g.AddComponent<TextMesh>();t.text=new[]{"LOW","MID","HIGH"}[i];t.fontSize=48;t.characterSize=.024f;t.anchor=TextAnchor.MiddleCenter;t.color=new Color(.74f,.80f,.83f);g.transform.position=new Vector3(-.6f+i*.6f,.002f,-1.50f);g.transform.rotation=Quaternion.Euler(90,180,0);}
  DetailBox("Field plinth",new Vector3(0,-.085f,0),new Vector3(3.72f,.07f,3.72f),new Color(.06f,.085f,.115f));
 }
 void SetPoses(){pg_poses(poses);foreach(var pair in bodies){int k=pair.Key*7;pair.Value.SetPositionAndRotation(new Vector3((float)poses[k],(float)poses[k+2],(float)poses[k+1]),new Quaternion(-(float)poses[k+4],-(float)poses[k+6],-(float)poses[k+5],(float)poses[k+3]));}pg_status(status);}
 float Key(KeyCode a,KeyCode b){return(Input.GetKey(a)?1:0)-(Input.GetKey(b)?1:0);}
 void Update(){if(poses==null)return;float dt=Time.unscaledDeltaTime;if(firstFrame){firstFrame=false;dt=0;wallClock.Restart();}elapsed+=dt;if(dt>0)fps=Mathf.Lerp(fps,1/Mathf.Max(dt,.0001f),.05f);
  if(Input.GetKeyDown(KeyCode.R)){if(stadium)ResetStadium();else ResetScene(scene);}if(Input.GetKeyDown(KeyCode.Space))paused=!paused;if(Input.GetKeyDown(KeyCode.H))help=!help;
  if(Input.GetKeyDown(KeyCode.Alpha4))SetStadium(!stadium);if(Input.GetKeyDown(KeyCode.Alpha1))SelectView(0);if(Input.GetKeyDown(KeyCode.Alpha2))SelectView(1);if(Input.GetKeyDown(KeyCode.Alpha3))SelectView(2);if(Input.GetKeyDown(KeyCode.T)&&!stadium){demo=!demo;if(demo)ResetScene(scene);}if(Input.GetKeyDown(KeyCode.F1)){demo=false;ResetScene(0);}if(Input.GetKeyDown(KeyCode.F2)){demo=false;ResetScene(1);}if(Input.GetKeyDown(KeyCode.F3)){demo=false;ResetScene(2);}if(Input.GetKeyDown(KeyCode.Escape))demo=false;
  if(Input.GetKeyDown(KeyCode.F12))ScreenCapture.CaptureScreenshot(Path.Combine(evidence,"playground-"+DateTime.Now.ToString("HHmmss")+".png"));
  float f=Key(KeyCode.W,KeyCode.S),t=Key(KeyCode.A,KeyCode.D),l=Key(KeyCode.E,KeyCode.Q),j=Key(KeyCode.X,KeyCode.Z),roll=Key(KeyCode.F,KeyCode.G);
  if(Input.GetKey(KeyCode.UpArrow))f=1;if(Input.GetKey(KeyCode.DownArrow))f=-1;if(Input.GetKey(KeyCode.LeftArrow))t=1;if(Input.GetKey(KeyCode.RightArrow))t=-1;
  if(demo){double phase=status[0]%24;f=phase>8&&phase<9?-.3f:0;j=phase>1&&phase<2.5?-1:phase>6&&phase<7.5?1:0;l=phase>3&&phase<4.5?1:phase>10&&phase<11.5?-1:0;roll=phase>1&&phase<2.5?1:0;t=phase>13&&phase<15?.3f:0;}
  pg_command(f,t,l,j,roll);timer.Restart();int steps=0;
  if(!paused){accumulator+=dt;while(accumulator>=.002&&steps<50){pg_step(1);accumulator-=.002;steps++;}stepsTotal+=steps;}else accumulator=0;
  maxBacklog=Math.Max(maxBacklog,accumulator);timer.Stop();physicsMs=(float)timer.Elapsed.TotalMilliseconds;SetPoses();SetCamera(false);
  if(elapsed>5){frames.Add(dt*1000);costs.Add(physicsMs);if(dt>.05f)slowFrames.Add(new SlowFrame{elapsedSeconds=elapsed,frameMs=dt*1000,physicsMs=physicsMs,previousPhysicsMs=previousPhysics,contacts=status[1],previousContacts=previousContacts,simulationSeconds=status[0]});}previousPhysics=physicsMs;previousContacts=status[1];metricClock+=dt;
  if(automated&&captureBenchmark&&!screenshotTaken&&elapsed>(startupCheck?.5f:8)){screenshotTaken=true;ScreenCapture.CaptureScreenshot(Path.Combine(evidence,"prototype.png"));}
  if(automated&&elapsed>=autoDuration){WriteMetrics();Application.Quit();}
 }
 // A background application must not keep executing the last held controls.
 // Automated benchmark runs explicitly exercise background stepping.
 void OnApplicationFocus(bool focused){if(!focused&&!automated)StopForFocusLoss();}
 void OnApplicationPause(bool suspended){if(suspended&&!automated)StopForFocusLoss();}
 void StopForFocusLoss(){paused=true;demo=false;accumulator=0;if(poses!=null)pg_command(0,0,0,0,0);}
 void SetCamera(bool immediate){if(cam==null)return;ui=Mathf.Max(.8f,Screen.height/820f);float left=panel*ui/Screen.width;cam.rect=new Rect(left,0,1-left,1);
  if(Input.GetMouseButton(1)){yaw+=Input.GetAxis("Mouse X")*3;pitch=Mathf.Clamp(pitch-Input.GetAxis("Mouse Y")*2,15,88);}zoomTarget=Mathf.Clamp(zoomTarget-Input.mouseScrollDelta.y*.14f,1.05f,stadium?11:7);distance=Mathf.Lerp(distance,zoomTarget,immediate?1:.15f);
  Vector3 target=view==1?bodies[robotId].position+Vector3.up*.22f:focus;cam.orthographic=view==2;if(view==2){cam.orthographicSize=stadium?3.35f:Mathf.Max(2.8f,2.05f/cam.aspect);cam.transform.position=new Vector3(0,5,0);cam.transform.rotation=Quaternion.Euler(90,180,0);}else{Vector3 pos=target+Quaternion.Euler(-pitch,yaw,0)*new Vector3(0,0,distance);cam.transform.position=immediate?pos:Vector3.Lerp(cam.transform.position,pos,.16f);cam.transform.LookAt(target);}
 }
 void SelectView(int selected){view=selected;zoomTarget=stadium?(view==1?2.0f:8.6f):view==1?1.8f:5.9f;}
 bool LoadPhysicsModel(bool field){
  var msg=new StringBuilder(4096);int n=pg_load(Path.Combine(Application.streamingAssetsPath,field?"stadium.xml":"playground.xml"),msg,4096);
  if(n==0){error="Unable to load the field: "+msg;paused=true;poses=null;return false;}
  poses=new double[n*7];robotId=pg_body("robot");bodies.Clear();foreach(var pair in bodyTransforms){int id=pair.Key=="world"?0:pg_body(pair.Key);if(id>=0)bodies[id]=pair.Value;}
  accumulator=0;return true;
 }
 void SetStadium(bool enabled){
  if(enabled!=stadium){if(!LoadPhysicsModel(enabled))return;stadium=enabled;inventory.Reset();}
  if(enabled&&!stadiumPiecesLoaded){FieldScenario.Validate(Application.streamingAssetsPath);LoadMeshes("StadiumPieces");stadiumPiecesLoaded=true;}
  demo=false;paused=enabled||startupCheck;
  foreach(var group in meshGroups)foreach(var renderer in group.Value)renderer.enabled=group.Key=="Robot"||(enabled?(group.Key=="Stadium"||group.Key=="StadiumPieces"):(group.Key=="Field"||group.Key=="ReusedPieces"));
  foreach(var go in practiceDetails)go.SetActive(!enabled);SelectView(enabled?0:view);focus=new Vector3(0,.10f,0);SetPoses();
 }
 void ResetStadium(){inventory.Reset();pg_reset(0);accumulator=0;paused=false;SetPoses();}
 void ResetScene(int selected){if(stadium)SetStadium(false);scene=selected;inventory.Reset();pg_reset(scene);accumulator=0;paused=false;SetPoses();}
 void InitGUI(){if(white!=null)return;white=Texture2D.whiteTexture;font=Font.CreateDynamicFontFromOSFont("Arial",18);title=new GUIStyle{font=font,fontSize=30,fontStyle=FontStyle.Bold,normal={textColor=Color.white}};body=new GUIStyle{font=font,fontSize=14,wordWrap=true,normal={textColor=new Color(.76f,.81f,.86f)}};small=new GUIStyle(body){fontSize=12};kicker=new GUIStyle(body){fontSize=11,fontStyle=FontStyle.Bold,normal={textColor=new Color(.38f,.80f,.80f)}};button=new GUIStyle(GUI.skin.button){font=font,fontSize=13,alignment=TextAnchor.MiddleLeft,padding=new RectOffset(14,8,8,8)};stat=new GUIStyle(title){fontSize=24};}
 void Rect(float x,float y,float w,float h,Color c){GUI.color=c;GUI.DrawTexture(new Rect(x,y,w,h),white);GUI.color=Color.white;}
 void Label(float x,float y,float w,float h,string txt,GUIStyle s){GUI.Label(new Rect(x,y,w,h),txt,s);}
 bool Button(float y,string text,bool active=false){GUI.backgroundColor=active?new Color(.23f,.70f,.70f):new Color(.24f,.30f,.37f);return GUI.Button(new Rect(24,y,232,36),text,button);}
 void OnGUI(){InitGUI();if(error!=""){GUI.Label(new Rect(30,30,Mathf.Max(300,Screen.width-60),300),error,body);if(GUI.Button(new Rect(30,350,180,40),"Close application"))Application.Quit();return;}GUI.matrix=Matrix4x4.Scale(new Vector3(ui,ui,1));float width=Screen.width/ui,height=Screen.height/ui;
  Rect(0,0,panel,height,new Color(.045f,.065f,.09f));Rect(panel,0,1,height,new Color(.17f,.23f,.29f));
  Label(24,28,240,22,"169C  /  ROBOTICS LAB",kicker);Label(22,61,245,45,"OVERRIDE",title);Label(24,103,230,36,"Robot practice & stadium",body);Rect(24,153,232,1,new Color(.18f,.23f,.28f));
  Label(24,177,230,20,"PRACTICE SETUP",kicker);for(int i=0;i<3;i++)if(Button(207+i*43,sceneNames[i]+"  [F"+(i+1)+"]",scene==i&&!stadium)){demo=false;ResetScene(i);}
  if(Button(348,"↺   Reset scene    [R]")){if(stadium)ResetStadium();else ResetScene(scene);}if(Button(391,paused?"▶   Resume    [Space]":"Ⅱ   Pause    [Space]",paused))paused=!paused;GUI.enabled=true;
  Label(24,459,230,20,"CAMERA",kicker);string[] views={"Overview  [1]","Follow robot  [2]","Top view  [3]"};for(int i=0;i<3;i++)if(Button(488+i*40,views[i],view==i)){SelectView(i);}
  GUI.enabled=!stadium;if(Button(621,demo?"Stop demonstration  [T]":"Run demonstration  [T]",demo)){demo=!demo;if(demo)ResetScene(scene);}GUI.enabled=true;if(Button(664,"Stadium development  [4]",stadium))SetStadium(!stadium);
  Label(24,height-113,235,34,stadium?"STADIUM  ·  DEVELOPMENT":"PROTOTYPE  ·  ESTIMATED PHYSICS",kicker);Label(24,height-81,230,62,stadium?"73 physical pieces. Field accuracy, loading, toggles and scoring are still under validation.":"CAD-based geometry. Mass, friction and actuator settings await hardware calibration.",small);
  Rect(panel+20,20,width-panel-40,54,new Color(.045f,.065f,.09f,.91f));Label(panel+36,30,310,22,stadium?"Override stadium":sceneNames[scene],body);Label(panel+36,51,420,18,stadium?"9 goals  ·  4 toggles  ·  4 loaders":"12 pins  ·  6 cups  ·  3 practice targets",small);
  string live=paused?"PAUSED":accumulator>.1?"BEHIND REAL TIME":"LIVE";Label(width-233,30,215,30,live+"   /   "+Mathf.RoundToInt(fps)+" fps",kicker);Label(width-233,51,215,20,"Q/E lift  ·  Z/X claw",small);
  if(help){Rect(panel+20,height-98,width-panel-40,78,new Color(.045f,.065f,.09f,.93f));Label(panel+36,height-86,width-panel-70,25,"W A S D  drive     Q / E  lower / raise     Z / X  close / open     F / G  rollers",body);Label(panel+36,height-57,width-panel-70,25,"Pickup: Q lower → X open → approach → Z + F grip/intake → E lift",small);}

  if(error!="")Label(panel+30,120,width-panel-60,400,error,body);
 }
 [Serializable] class Metrics{public string engine="MuJoCo 3.13.0",unity;public bool startupCheck,stadium,benchmark,scriptedCommands;public float wallSeconds,simulationSeconds,frameP50ms,frameP95ms,frameP99ms,frameMaxms,physicsP99ms;public float physicsMaxms;public SlowFrame[] slowFrames;public int framesOver50ms,frames;public double badAcceleration,badPosition,backlogSeconds,maxBacklogSeconds,measuredWallSeconds;public int scenario,pixelWidth,pixelHeight;}
 float Percentile(List<float> a,float p){if(a.Count==0)return 0;var v=a.ToArray();Array.Sort(v);return v[Mathf.Min(v.Length-1,(int)(p*(v.Length-1)))];}
 void WriteMetrics(){var m=new Metrics{benchmark=benchmark,scriptedCommands=demo,stadium=stadium,physicsMaxms=Percentile(costs,1),slowFrames=slowFrames.ToArray(),startupCheck=startupCheck,unity=Application.unityVersion,wallSeconds=elapsed,simulationSeconds=(float)status[0],frameP50ms=Percentile(frames,.50f),frameP95ms=Percentile(frames,.95f),frameP99ms=Percentile(frames,.99f),frameMaxms=Percentile(frames,1),physicsP99ms=Percentile(costs,.99f),frames=frames.Count,framesOver50ms=frames.FindAll(v=>v>50).Count,badAcceleration=status[8],badPosition=status[9],backlogSeconds=accumulator,maxBacklogSeconds=maxBacklog,measuredWallSeconds=wallClock.Elapsed.TotalSeconds,scenario=scene,pixelWidth=Screen.width,pixelHeight=Screen.height};File.WriteAllText(Path.Combine(evidence,"metrics-"+DateTime.Now.ToString("HHmmss")+".json"),JsonUtility.ToJson(m,true));}
 void OnApplicationQuit(){if(poses!=null){WriteMetrics();pg_close();}}
}
