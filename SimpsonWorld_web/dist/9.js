webpackJsonp([9],{

/***/ 404:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
Object.defineProperty(__webpack_exports__, "__esModule", { value: true });
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_0__babel_loader_node_modules_vue_loader_lib_selector_type_script_index_0_user_vue__ = __webpack_require__(557);
/* harmony import */ var __WEBPACK_IMPORTED_MODULE_1__node_modules_vue_loader_lib_template_compiler_index_id_data_v_6908d32b_hasScoped_false_buble_transforms_node_modules_vue_loader_lib_selector_type_template_index_0_user_vue__ = __webpack_require__(650);
function injectStyle (ssrContext) {
  __webpack_require__(671)
}
var normalizeComponent = __webpack_require__(3)
/* script */

/* template */

/* template functional */
  var __vue_template_functional__ = false
/* styles */
var __vue_styles__ = injectStyle
/* scopeId */
var __vue_scopeId__ = null
/* moduleIdentifier (server only) */
var __vue_module_identifier__ = null
var Component = normalizeComponent(
  __WEBPACK_IMPORTED_MODULE_0__babel_loader_node_modules_vue_loader_lib_selector_type_script_index_0_user_vue__["a" /* default */],
  __WEBPACK_IMPORTED_MODULE_1__node_modules_vue_loader_lib_template_compiler_index_id_data_v_6908d32b_hasScoped_false_buble_transforms_node_modules_vue_loader_lib_selector_type_template_index_0_user_vue__["a" /* default */],
  __vue_template_functional__,
  __vue_styles__,
  __vue_scopeId__,
  __vue_module_identifier__
)

/* harmony default export */ __webpack_exports__["default"] = (Component.exports);


/***/ }),

/***/ 557:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//
//

/* harmony default export */ __webpack_exports__["a"] = ({
    data() {
        return this.$store.getters.profile;
    },
    methods: {},
    created() {
        this.$message({
            message: '欢迎加入simpson！'
        });
    }
});

/***/ }),

/***/ 573:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(8)(undefined);
// imports


// module
exports.push([module.i, ".sidebar{height:100%}", ""]);

// exports


/***/ }),

/***/ 650:
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
var render = function () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('el-container',[_c('el-aside',[_c('el-menu',{staticClass:"sidebar",attrs:{"router":"true","default-active":_vm.$route.path}},[_c('el-menu-item',{attrs:{"index":"/my/posts"}},[_vm._v("\n            我的发布\n        ")]),_vm._v(" "),_c('el-menu-item',{attrs:{"index":"/my/messages"}},[_vm._v("\n            私信\n        ")]),_vm._v(" "),_c('el-menu-item',{attrs:{"index":"/my/setting"}},[_vm._v("\n            个人信息\n        ")]),_vm._v(" "),_c('el-menu-item',{attrs:{"index":"/my/collections"}},[_vm._v("\n            我的收藏\n        ")]),_vm._v(" "),_c('el-menu-item',{attrs:{"index":"/my/updatepwd"}},[_vm._v("\n            修改密码\n        ")])],1)],1),_vm._v(" "),_c('router-view')],1)}
var staticRenderFns = []
var esExports = { render: render, staticRenderFns: staticRenderFns }
/* harmony default export */ __webpack_exports__["a"] = (esExports);

/***/ }),

/***/ 671:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(573);
if(typeof content === 'string') content = [[module.i, content, '']];
if(content.locals) module.exports = content.locals;
// add the styles to the DOM
var update = __webpack_require__(10)("741c297b", content, true);

/***/ })

});
//# sourceMappingURL=9.js.map?7030e89df9541a1d7915