using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

// Schema shared with Tools/generate_field_scenario.py. Coordinates are native SI.
public static class FieldScenario {
 [Serializable] public sealed class Piece {public string id,kind,alliance,state;public bool clearSideUp;public double[] position,quaternion;}
 [Serializable] public sealed class Scenario {public Piece[] pieces;public string status;}
 public static void Validate(string assets){
  var scene=JsonUtility.FromJson<Scenario>(File.ReadAllText(Path.Combine(assets,"StadiumPieces/scenario.json")));
  var ledger=new FieldInventory();var byId=new Dictionary<string,FieldInventory.Piece>();foreach(var p in ledger.Pieces)byId.Add(p.Id,p);
  if(scene==null||scene.pieces==null||scene.pieces.Length!=119)throw new Exception("Field setup must account for all 119 pieces.");
  var seen=new HashSet<string>();int active=0;
  foreach(var p in scene.pieces){
   FieldInventory.Piece expected;
   if(!seen.Add(p.id)||!byId.TryGetValue(p.id,out expected)||expected.Kind!=p.kind||expected.Alliance!=p.alliance||expected.ClearSideUp!=p.clearSideUp||expected.State.ToString()!=p.state)throw new Exception("Field setup inventory mismatch: "+p.id);
   if(p.state!="Field")continue;active++;
   if(p.position==null||p.position.Length!=3||p.quaternion==null||p.quaternion.Length!=4)throw new Exception("Missing physical pose: "+p.id);
   double norm=0;foreach(double v in p.position)if(double.IsNaN(v)||double.IsInfinity(v))throw new Exception("Invalid field position: "+p.id);
   foreach(double v in p.quaternion){if(double.IsNaN(v)||double.IsInfinity(v))throw new Exception("Invalid field rotation: "+p.id);norm+=v*v;}
   if(Math.Abs(norm-1)>.000001)throw new Exception("Non-unit field rotation: "+p.id);
  }
  if(active!=73)throw new Exception("Field setup must contain 73 active objects.");
 }
}
