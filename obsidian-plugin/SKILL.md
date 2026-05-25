---
name: obsidian-plugin
description: 用于开发 Obsidian 插件的技能。包含 TypeScript 项目结构、Plugin/PluginSettingTab 模式、自定义视图 (ItemView)、命令注册、事件处理、设置管理、工厂模式、esbuild 打包配置等最佳实践。当用户要求创建或修改 Obsidian 插件时自动激活。
---
# Obsidian 插件开发指南

本技能总结了开发 Obsidian 插件时的代码模式、项目结构和最佳实践。

## 项目结构

```
obsidian-plugin-name/
├── manifest.json           # 插件元数据 (必须)
├── main.js                 # 打包后的入口文件 (必须)
├── styles.css              # 插件样式 (可选)
├── package.json            # npm 配置
├── tsconfig.json           # TypeScript 配置
├── esbuild.config.mjs      # esbuild 打包配置
└── src/
    ├── main.ts             # 主插件类
    ├── settings.ts         # 设置接口和设置标签页
    ├── types.ts            # TypeScript 类型定义
    ├── [feature]/          # 功能模块文件夹
    │   ├── base.ts         # 接口定义
    │   ├── factory.ts      # 工厂类
    │   └── [impl].ts       # 具体实现
    └── utils/              # 工具函数
```

## manifest.json 模板

{
    "id": "plugin-id",
    "name": "Plugin Name",
    "version": "1.0.0",
    "minAppVersion": "0.1.0",
    "description": "插件描述",
    "author": "fisher",
    "authorUrl": "https://fisheryounggod.github.io",
    "isDesktopOnly": false
}

## 主插件类模式 (main.ts)

```typescript
import { Plugin, Notice, Menu, Editor, MarkdownView, WorkspaceLeaf } from 'obsidian';
import { MyPluginSettingTab, DEFAULT_SETTINGS, MyPluginSettings } from './settings';

export default class MyPlugin extends Plugin {
    settings: MyPluginSettings;
  
    // 其他组件实例
    private someComponent: SomeComponent;

    async onload() {
        // 1. 加载设置
        await this.loadSettings();
      
        // 2. 初始化组件
        this.someComponent = new SomeComponent();
      
        // 3. 注册视图
        this.registerView(
            VIEW_TYPE_CONSTANT,
            (leaf) => new MyCustomView(leaf, this)
        );
      
        // 4. 添加 Ribbon 图标
        this.addRibbonIcon('icon-name', '提示文字', () => {
            // 点击处理
        });
      
        // 5. 注册命令
        this.addCommand({
            id: 'command-id',
            name: 'Command Name',
            callback: () => {
                // 命令逻辑
            },
            hotkeys: [{ modifiers: ['Mod'], key: 'k' }]  // 可选快捷键
        });
      
        // 6. 添加设置标签页
        this.addSettingTab(new MyPluginSettingTab(this.app, this));
      
        // 7. 注册事件
        this.registerEvent(
            this.app.workspace.on('editor-menu', (menu, editor, view) => {
                // 右键菜单处理
            })
        );
      
        // 8. 注册 DOM 事件
        this.registerDomEvent(document.body, 'click', (evt) => {
            // DOM 事件处理
        });
      
        console.log('Plugin loaded');
    }

    onunload() {
        // 清理资源
        this.app.workspace.detachLeavesOfType(VIEW_TYPE_CONSTANT);
        console.log('Plugin unloaded');
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }
  
    // 激活视图的通用方法
    async activateView(viewType: string) {
        const existing = this.app.workspace.getLeavesOfType(viewType);
        if (existing.length === 0) {
            await this.app.workspace.getRightLeaf(false)?.setViewState({
                type: viewType,
                active: true,
            });
        }
        this.app.workspace.revealLeaf(this.app.workspace.getLeavesOfType(viewType)[0]);
    }
}
```

## 设置管理模式 (settings.ts)

```typescript
import { App, PluginSettingTab, Setting } from 'obsidian';
import type MyPlugin from './main';

// 设置接口 - 定义所有配置项
export interface MyPluginSettings {
    option1: string;
    option2: boolean;
    nestedSettings: {
        enabled: boolean;
        value: number;
    };
}

// 默认设置 - 必须提供完整的默认值
export const DEFAULT_SETTINGS: MyPluginSettings = {
    option1: 'default',
    option2: true,
    nestedSettings: {
        enabled: false,
        value: 100,
    },
};

// 设置标签页类
export class MyPluginSettingTab extends PluginSettingTab {
    plugin: MyPlugin;

    constructor(app: App, plugin: MyPlugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        const { containerEl } = this;
        containerEl.empty();

        // 分组标题
        containerEl.createEl('h2', { text: '基本设置' });

        // 下拉选择
        new Setting(containerEl)
            .setName('选项1')
            .setDesc('选项描述')
            .addDropdown((dropdown) =>
                dropdown
                    .addOption('value1', '显示名1')
                    .addOption('value2', '显示名2')
                    .setValue(this.plugin.settings.option1)
                    .onChange(async (value) => {
                        this.plugin.settings.option1 = value;
                        await this.plugin.saveSettings();
                    })
            );

        // 开关
        new Setting(containerEl)
            .setName('选项2')
            .addToggle((toggle) =>
                toggle
                    .setValue(this.plugin.settings.option2)
                    .onChange(async (value) => {
                        this.plugin.settings.option2 = value;
                        await this.plugin.saveSettings();
                        this.display();  // 重新渲染以显示/隐藏条件设置
                    })
            );

        // 条件显示设置
        if (this.plugin.settings.option2) {
            new Setting(containerEl)
                .setName('条件设置')
                .addSlider((slider) =>
                    slider
                        .setLimits(0, 100, 10)
                        .setValue(this.plugin.settings.nestedSettings.value)
                        .setDynamicTooltip()
                        .onChange(async (value) => {
                            this.plugin.settings.nestedSettings.value = value;
                            await this.plugin.saveSettings();
                        })
                );
        }

        // 文本输入
        new Setting(containerEl)
            .setName('文本设置')
            .addText((text) =>
                text
                    .setPlaceholder('placeholder')
                    .setValue(this.plugin.settings.option1)
                    .onChange(async (value) => {
                        this.plugin.settings.option1 = value;
                        await this.plugin.saveSettings();
                    })
            );

        // 多行文本
        new Setting(containerEl)
            .setName('多行文本')
            .addTextArea((text) =>
                text
                    .setPlaceholder('placeholder')
                    .setValue(this.plugin.settings.option1)
                    .onChange(async (value) => {
                        this.plugin.settings.option1 = value;
                        await this.plugin.saveSettings();
                    })
            );
    }
}
```

## 自定义视图模式 (ItemView)

```typescript
import { ItemView, WorkspaceLeaf } from 'obsidian';

export const MY_VIEW_TYPE = 'my-custom-view';

export class MyCustomView extends ItemView {
    private containerEl: HTMLElement;

    constructor(leaf: WorkspaceLeaf) {
        super(leaf);
    }

    getViewType(): string {
        return MY_VIEW_TYPE;
    }

    getDisplayText(): string {
        return '视图标题';
    }

    getIcon(): string {
        return 'file-text';  // Lucide 图标名
    }

    async onOpen() {
        this.containerEl = this.contentEl;
        this.containerEl.empty();
        this.containerEl.addClass('my-view-container');
      
        // 构建 UI
        this.containerEl.createEl('h3', { text: '标题' });
        const content = this.containerEl.createDiv({ cls: 'my-content' });
        // ...
    }

    async onClose() {
        // 清理
        this.containerEl.empty();
    }
  
    // 公共方法供外部调用
    setContent(html: string): void {
        this.containerEl.innerHTML = html;
    }
}
```

## 工厂模式

```typescript
// base.ts - 接口定义
export interface ProviderInterface {
    getName(): string;
    process(input: string): Promise<Result>;
}

// factory.ts - 工厂类
import { ProviderInterface } from './base';
import { ImplementationA } from './impl-a';
import { ImplementationB } from './impl-b';

export class ProviderFactory {
    static create(type: string): ProviderInterface {
        switch (type) {
            case 'typeA':
                return new ImplementationA();
            case 'typeB':
                return new ImplementationB();
            default:
                return new ImplementationA();
        }
    }
}
```

## esbuild 打包配置

```javascript
import esbuild from "esbuild";
import process from "process";
import builtins from "builtin-modules";

const banner = `/*
THIS IS A GENERATED/BUNDLED FILE BY ESBUILD
if you want to view the source, please visit the github repository of this plugin
*/
`;

const prod = (process.argv[2] === 'production');

const context = await esbuild.context({
    banner: { js: banner },
    entryPoints: ['src/main.ts'],
    bundle: true,
    external: [
        'obsidian',
        'electron',
        '@codemirror/autocomplete',
        '@codemirror/collab',
        '@codemirror/commands',
        '@codemirror/language',
        '@codemirror/lint',
        '@codemirror/search',
        '@codemirror/state',
        '@codemirror/view',
        '@lezer/common',
        '@lezer/highlight',
        '@lezer/lr',
        ...builtins
    ],
    format: 'cjs',
    target: 'es2018',
    logLevel: "info",
    sourcemap: prod ? false : 'inline',
    treeShaking: true,
    outfile: 'main.js',
});

if (prod) {
    await context.rebuild();
    process.exit(0);
} else {
    await context.watch();
}
```

## package.json 模板

```json
{
    "name": "obsidian-plugin-name",
    "version": "1.0.0",
    "description": "Plugin description",
    "main": "main.js",
    "scripts": {
        "dev": "node esbuild.config.mjs",
        "build": "tsc -noEmit -skipLibCheck && node esbuild.config.mjs production"
    },
    "devDependencies": {
        "@types/node": "^16.11.6",
        "builtin-modules": "3.3.0",
        "esbuild": "0.17.3",
        "obsidian": "latest",
        "tslib": "2.4.0",
        "typescript": "4.7.4"
    }
}
```

## tsconfig.json 模板

```json
{
    "compilerOptions": {
        "baseUrl": ".",
        "inlineSourceMap": true,
        "inlineSources": true,
        "module": "ESNext",
        "target": "ES6",
        "allowJs": true,
        "noImplicitAny": true,
        "moduleResolution": "node",
        "importHelpers": true,
        "isolatedModules": true,
        "strictNullChecks": true,
        "lib": ["DOM", "ES5", "ES6", "ES7"]
    },
    "include": ["**/*.ts"]
}
```

## 常用 API 模式

### 获取当前编辑器

```typescript
const activeView = this.app.workspace.getActiveViewOfType(MarkdownView);
if (activeView) {
    const editor = activeView.editor;
    const content = editor.getValue();
    const selection = editor.getSelection();
    editor.setValue(newContent);
}
```

### 文件操作

```typescript
// 读取文件
const file = this.app.vault.getAbstractFileByPath('path/to/file.md');
if (file instanceof TFile) {
    const content = await this.app.vault.read(file);
}

// 创建文件
await this.app.vault.create('path/to/new.md', content);

// 修改文件
await this.app.vault.modify(file, newContent);
```

### Modal 对话框

```typescript
import { Modal, App } from 'obsidian';

class MyModal extends Modal {
    result: string;
    onSubmit: (result: string) => void;

    constructor(app: App, onSubmit: (result: string) => void) {
        super(app);
        this.onSubmit = onSubmit;
    }

    onOpen() {
        const { contentEl } = this;
        contentEl.createEl('h2', { text: '标题' });
      
        const input = contentEl.createEl('input', { type: 'text' });
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.onSubmit(input.value);
                this.close();
            }
        });
    }

    onClose() {
        const { contentEl } = this;
        contentEl.empty();
    }
}
```

### 通知

```typescript
import { Notice } from 'obsidian';

// 临时通知
new Notice('操作完成');

// 持久通知
const notice = new Notice('加载中...', 0);  // 0 = 不自动关闭
// 完成后手动关闭
notice.hide();
```

## 开发流程

1. **初始化项目**: 复制模板文件 (manifest.json, package.json, tsconfig.json, esbuild.config.mjs)
2. **安装依赖**: `npm install`
3. **开发模式**: `npm run dev` (自动监听变化并重新打包)
4. **测试**: 在 Obsidian 中启用开发者模式，加载本地插件
5. **生产构建**: `npm run build`

## 调试技巧

- 使用 `console.log()` 输出调试信息，在开发者工具 (Ctrl/Cmd+Shift+I) 中查看
- 使用 `new Notice()` 显示临时消息
- 在 Obsidian 设置中启用 "Hot Reload" 社区插件可自动重载

## CSS 样式命名约定

- 使用插件前缀避免冲突: `.my-plugin-container`
- 遵循 BEM 命名: `.my-plugin-button--active`
- 样式放在 `styles.css` 文件中
