# BPM: Project Manager Survival Kit for Blender

## Who is this for?

For anyone opening Blender for the first time thinking: "Where do I save my file? What does linking mean? Why did my texture disappear overnight?" This guide starts from zero and goes all the way to the tricks used by large studios, all applied to the BPM suite (Blender Production Manager).

## 0 · Why does structure matter?

Imagine your project is a complex LEGO model. If you dump all the pieces on the floor, you’ll soon lose track of how they connect. A project’s structure is like the instruction manual: it defines where everything lives, how it relates to other parts, and how to find it without wasting time.

**Organization ≠ Rigidity**: It's the skeleton that lets you move your arms without falling apart. This skeleton can grow and adapt to support a larger, more complex body.

**Structure = Speed**: With an organized project, you open the right file, make your change, and close it—without spending hours hunting for "that working version of the rig from yesterday."

The BPM suite will help you automate and simplify this order, but first, you need to understand the concepts.

## 1 · Full Anatomy of an Animation Project

A 3D project is usually divided into three major acts—think of them as preparing, cooking, and serving.

### 1.1 Pre-production – "Preparing the ingredients"

This is the planning phase. It includes:

* **Concept and Script**
* **Concept Art and Design**
* **Storyboard**
* **Animatic**

### 1.2 Production – "Cooking the main dish"

This is where Blender and BPM become your best friends. Modeling, texturing, animating, lighting, and rendering.

#### 1.2.1 Folder Tree

**How to use it:**

* File > Project Management > Plant the Tree
* Choose project location
* Customize the needed folders

Example structure:

```
/ProjectName/
├── 01_Pre-production/
│   ├── Script/
│   ├── Concept Art/
│   └── Storyboard/
├── 02_Production/
│   ├── Assets/
│   │   ├── Models/
│   │   │   ├── Characters/
│   │   │   ├── Scenarios/
│   │   │   └── Props/
│   ├── Scenes (Layout)/
│   ├── Animation/
│   └── Libraries/
│       ├── Textures/
│       ├── Addons/
│       └── Temp/
└── 03_Post-production/
    ├── Renders/
    ├── Editing/
    └── Exports/
```

#### 1.2.2 Asset Lifecycle

**Step 1: Master File (Placeholder)**

* Create collection: `00_Pepito_main`
* Save as `Pepito.blend`

**Step 2: Incremental Versions vs. Backups**

* Daily work: `Pepito_001.blend`, `Pepito_002.blend`, etc.
* Master: `Pepito.blend`
* Backups: `.blend1`, `.blend2`

**Pro Tip**: Edit > Preferences > Save Versions: set it to 6

**Step 3: BPM Naming Convention**
`[BRANCH]_[NAME]-[DETAILS]_[VERSION].blend`

Example:
`02_Scene_26_shot_023-156_005.blend`

#### 1.2.3 Link vs. Append vs. Override

* **Link 🔗**: External, synchronized data
* **Append 📥**: Local copy
* **Override 🛠️**: Editable linked data

#### 1.2.4 .blend as Container

* Use the **Fake User (F)** to preserve unused data-blocks

#### 1.2.5 External Files & Textures

* Define root with BPA: Select Project Root Folder
* Use: Textures to Current Directory

#### 1.2.6 Recovery and Temp Files

* BPA: Save Temp in Project Tree

#### 1.2.7 Link Health

* Traffic light diagnosis: Green, Yellow, Red

#### 1.2.8 Packing for Travel

* **File > External Data > Pack Resources**
* Use **Unpack Resources** to restore links

## 2 · From Artist to Supervisor: BPM Reporting System

### 2.1 The Artist

* BPA Panel > Asset Status
* Fill in fields (Type, Process, State, Assigned To, Note)
* Save Report: generates `01_pepito report.csv`

### 2.2 The Supervisor

* BPM > Overseer Dashboard
* Load CSV Reports
* Analyze and validate changes with Validate All Changes

## 3 · Advanced Topics & Best Practices

### 3.2 Modular Workflow

* Separate assets and scenes
* Link as much as possible

### 3.3 Survival Checklist

* [ ] Define project root with BPM at the start
* [ ] Avoid to move files using OS file explorer
* [ ] Use relative paths
* [ ] Set high Save Versions in preferences
* [ ] Use Fake User for important data-blocks
* [ ] Backup entire project regularly (e.g. zip it)

## Future Implementations

* Project templates from JSON
* Reconnect packed links
* Relocate outsiders
* Override resync/enforce
* Load .blend1/.blend2 backups
* Button to open referenced files in Overseer
