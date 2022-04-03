// @license magnet:?xt=urn:btih:0b31508aeb0634b347b8270c7bee4d411b5d4109&dn=agpl-3.0.txt AGPL-3.0
// API host/endpoint
var BaseUrl = window.location.protocol + "//" + window.location.host;
var htmlRegex = /<(.*)>.*?|<(.*)\/>/;
document.addEventListener('DOMContentLoaded', function(){
    var sidenavElems = document.querySelectorAll('.sidenav');
    var sidenavInstances = M.Sidenav.init(sidenavElems);

    var app = new Vue({
        el: '#app',
        delimiters: ['[[',']]'],
        data: {
            BaseUrl: BaseUrl,
            loading: true,
            error: "",
            langs: [],
            settings: {},
            sourceLang: "",
            targetLang: "",

            loadingTranslation: false,
            inputText: "",
            inputTextareaHeight: 250,
            savedTanslatedText: "",
            translatedText: "",
            output: "",
            charactersLimit: -1,

            copyTextLabel: "Copy text",

            suggestions: false,
            isSuggesting: false,

            supportedFilesFormat : [],
            translationType: "text",
            inputFile: false,
            loadingFileTranslation: false,
            translatedFileUrl: false,
            filesTranslation: true,
            frontendTimeout: 500
        },
        mounted: function(){
            var self = this;
            var requestSettings = new XMLHttpRequest();
            requestSettings.open('GET', BaseUrl + '/frontend/settings', true);

            requestSettings.onload = function() {
                if (this.status >= 200 && this.status < 400) {
                    // Success!
                    self.settings = JSON.parse(this.response);
                    self.sourceLang = self.settings.language.source.code;
                    self.targetLang = self.settings.language.target.code;
                    self.charactersLimit = self.settings.charLimit;
                    self.suggestions = self.settings.suggestions;
                    self.supportedFilesFormat = self.settings.supportedFilesFormat;
                    self.filesTranslation = self.settings.filesTranslation;
                    self.frontendTimeout = self.settings.frontendTimeout;
                }else {
                    self.error = "Cannot load /frontend/settings";
                    self.loading = false;
                }
            };

            requestSettings.onerror = function() {
                self.error = "Error while calling /frontend/settings";
                self.loading = false;
            };

            requestSettings.send();

            var requestLanguages = new XMLHttpRequest();
            requestLanguages.open('GET', BaseUrl + '/languages', true);

            requestLanguages.onload = function() {
                if (this.status >= 200 && this.status < 400) {
                    // Success!
                    self.langs = JSON.parse(this.response);
                    self.langs.push({ name: 'Auto Detect (Experimental)', code: 'auto' })
                    if (self.langs.length === 0){
                        self.loading = false;
                        self.error = "No languages available. Did you install the models correctly?"
                        return;
                    }

                    const sourceLanguage = self.langs.find(l => l.code === self.getQueryParam('source'))
                    const isSourceAuto = !sourceLanguage && self.getQueryParam('source') === "auto"
                    const targetLanguage = self.langs.find(l => l.code === self.getQueryParam('target'))

                    if (sourceLanguage || isSourceAuto) {
                        self.sourceLang = isSourceAuto ? "auto" : sourceLanguage.code
                    }

                    if (targetLanguage) {
                        self.targetLang = targetLanguage.code
                    }

                    const defaultText = self.getQueryParam('q')

                    if(defaultText) {
                        self.inputText = decodeURI(defaultText)
                    }

                    self.loading = false;
                } else {
                    self.error = "Cannot load /languages";
                    self.loading = false;
                }
            };

            requestLanguages.onerror = function() {
                self.error = "Error while calling /languages";
                self.loading = false;
            };

            requestLanguages.send();
        },
        updated: function(){
            M.FormSelect.init(this.$refs.sourceLangDropdown);
            M.FormSelect.init(this.$refs.targetLangDropdown);
            
            if (this.$refs.inputTextarea){
                if (this.inputText === ""){
                    this.$refs.inputTextarea.style.height = this.inputTextareaHeight + "px";
                    this.$refs.translatedTextarea.style.height = this.inputTextareaHeight + "px";
                }else{
                    this.$refs.inputTextarea.style.height = this.$refs.translatedTextarea.style.height = "1px";
                    this.$refs.inputTextarea.style.height = Math.max(this.inputTextareaHeight, this.$refs.inputTextarea.scrollHeight + 32) + "px";
                    this.$refs.translatedTextarea.style.height = Math.max(this.inputTextareaHeight, this.$refs.translatedTextarea.scrollHeight + 32) + "px";
                }
            }

            if (this.charactersLimit !== -1 && this.inputText.length >= this.charactersLimit){
                this.inputText = this.inputText.substring(0, this.charactersLimit);
            }

            // Update "selected" attribute (to overcome a vue.js limitation)
            // but properly display checkmarks on supported browsers.
            // Also change the <select> width value depending on the <option> length
            if (this.$refs.sourceLangDropdown){
                for (var i = 0; i < this.$refs.sourceLangDropdown.children.length; i++){
                    var el = this.$refs.sourceLangDropdown.children[i];
                    if (el.value === this.sourceLang){
                        el.setAttribute('selected', '');
                        this.$refs.sourceLangDropdown.style.width = getTextWidth(el.text) + 24 + 'px';
                    }else{
                        el.removeAttribute('selected');
                    }
                }
            }

            if (this.$refs.targetLangDropdown){
                for (var i = 0; i < this.$refs.targetLangDropdown.children.length; i++){
                    var el = this.$refs.targetLangDropdown.children[i];
                    if (el.value === this.targetLang){
                        el.setAttribute('selected', '');
                        this.$refs.targetLangDropdown.style.width = getTextWidth(el.text) + 24 + 'px';
                    }else{
                        el.removeAttribute('selected');
                    }
                }
            }
        },
        computed: {
            requestCode: function(){
                return ['const res = await fetch("' + this.BaseUrl + '/translate", {',
                    '	method: "POST",',
                    '	body: JSON.stringify({',
                    '		q: ' + this.$options.filters.escape(this.inputText) + ',',
                    '		source: ' + this.$options.filters.escape(this.sourceLang) + ',',
                    '		target: ' + this.$options.filters.escape(this.targetLang) + ',',
                    '		format: "' + (this.isHtml ? "html" : "text") + '"',
                    '	}),',
                    '	headers: { "Content-Type": "application/json" }',
                    '});',
                    '',
                    'console.log(await res.json());'].join("\n");
            },
            supportedFilesFormatFormatted: function() {
                return this.supportedFilesFormat.join(', ');
            },
            isHtml: function(){
                return htmlRegex.test(this.inputText);
            },
            canSendSuggestion() {
                return this.translatedText.trim() !== "" && this.translatedText !== this.savedTanslatedText;
            }
        },
        filters: {
            escape: function(v){
                return JSON.stringify(v);
            },
            highlight: function(v){
                return Prism.highlight(v, Prism.languages.javascript, 'javascript');
            }
        },
        methods: {
            abortPreviousTransRequest: function(){
                if (this.transRequest){
                    this.transRequest.abort();
                    this.transRequest = null;
                }
            },
            swapLangs: function(e){
                this.closeSuggestTranslation(e)

                var t = this.sourceLang;
                this.sourceLang = this.targetLang;
                this.targetLang = t;
                this.inputText = this.translatedText;
                this.translatedText = "";
                this.handleInput();
            },
            dismissError: function(){
                this.error = '';
            },
            getQueryParam: function (key) {
                const params = new URLSearchParams(window.location.search);
                return params.get(key)
            },
            updateQueryParam: function (key, value) {
                let searchParams = new URLSearchParams(window.location.search)
                searchParams.set(key, value);
                let newRelativePathQuery = window.location.pathname + '?' + searchParams.toString();
                history.pushState(null, '', newRelativePathQuery);
            },
            handleInput: function(e){
                this.closeSuggestTranslation(e)

                this.updateQueryParam('source', this.sourceLang)
                this.updateQueryParam('target', this.targetLang)
                this.updateQueryParam('q', encodeURI(this.inputText))

                if (this.timeout) clearTimeout(this.timeout);
                this.timeout = null;

                if (this.inputText === ""){
                    this.translatedText = "";
                    this.output = "";
                    this.abortPreviousTransRequest();
                    this.loadingTranslation = false;
                    return;
                }

                var self = this;

                self.loadingTranslation = true;
                this.timeout = setTimeout(function(){
                    self.abortPreviousTransRequest();

                    var request = new XMLHttpRequest();
                    self.transRequest = request;

                    var data = new FormData();
                    data.append("q", self.inputText);
                    data.append("source", self.sourceLang);
                    data.append("target", self.targetLang);
                    data.append("format", self.isHtml ? "html" : "text");
                    data.append("api_key", localStorage.getItem("api_key") || "");

                    request.open('POST', BaseUrl + '/translate', true);

                    request.onload = function() {
                        try{
                            var res = JSON.parse(this.response);
                            // Success!
                            if (res.translatedText !== undefined){
                                self.translatedText = res.translatedText;
                                self.loadingTranslation = false;
                                self.output = JSON.stringify(res, null, 4);
                            }else{
                                throw new Error(res.error || "Unknown error");
                            }
                        }catch(e){
                            self.error = e.message;
                            self.loadingTranslation = false;
                        }
                    };

                    request.onerror = function() {
                        self.error = "Error while calling /translate";
                        self.loadingTranslation = false;
                    };

                    request.send(data);
                }, self.frontendTimeout);
            },
            copyText: function(e){
                e.preventDefault();
                this.$refs.translatedTextarea.select();
                this.$refs.translatedTextarea.setSelectionRange(0, 9999999); /* For mobile devices */
                document.execCommand("copy");

                if (this.copyTextLabel === "Copy text"){
                    this.copyTextLabel = "Copied";
                    var self = this;
                    setTimeout(function(){
                        self.copyTextLabel = "Copy text";
                    }, 1500);
                }
            },
            suggestTranslation: function(e) {
                e.preventDefault();
                this.savedTanslatedText = this.translatedText

                this.isSuggesting = true;
            },
            closeSuggestTranslation: function(e) {
                this.translatedText = this.savedTanslatedText

                e.preventDefault();

                this.isSuggesting = false;
            },
            sendSuggestion: function(e) {
                e.preventDefault();

                var self = this;

                var request = new XMLHttpRequest();
                self.transRequest = request;

                var data = new FormData();
                data.append("q", self.inputText);
                data.append("s", self.translatedText);
                data.append("source", self.sourceLang);
                data.append("target", self.targetLang);
                data.append("api_key", localStorage.getItem("api_key") || "");

                request.open('POST', BaseUrl + '/suggest', true);
                request.onload = function() {
                    try{
                        var res = JSON.parse(this.response);
                        if (res.success){
                            M.toast({html: 'Thanks for your correction.'})
                            self.closeSuggestTranslation(e)
                        }else{
                            throw new Error(res.error || "Unknown error");
                        }
                    }catch(e){
                        self.error = e.message;
                        self.closeSuggestTranslation(e)
                    }
                };

                request.onerror = function() {
                    self.error = "Error while calling /suggest";
                    self.loadingTranslation = false;
                };

                request.send(data);
            },
            deleteText: function(e){
                e.preventDefault();
                this.inputText = this.translatedText = this.output = "";
                this.$refs.inputTextarea.focus();
            },
            switchType: function(type) {
                this.translationType = type;
            },
            handleInputFile: function(e) {
                this.inputFile = e.target.files[0];
            },
            removeFile: function(e) {
              e.preventDefault()
              this.inputFile = false;
              this.translatedFileUrl = false;
              this.loadingFileTranslation = false;
            },
            translateFile: function(e) {
                e.preventDefault();

                let self = this;
                let translateFileRequest = new XMLHttpRequest();

                translateFileRequest.open("POST", BaseUrl + "/translate_file", true);

                let data = new FormData();
                data.append("file", this.inputFile);
                data.append("source", this.sourceLang);
                data.append("target", this.targetLang);
                data.append("api_key", localStorage.getItem("api_key") || "");

                this.loadingFileTranslation = true

                translateFileRequest.onload = function()  {
                    if (translateFileRequest.readyState === 4 && translateFileRequest.status === 200) {
                        try{
                            self.loadingFileTranslation = false;

                            let res = JSON.parse(this.response);
                            if (res.translatedFileUrl){
                                self.translatedFileUrl = res.translatedFileUrl;

                                let link = document.createElement("a");
                                link.target = "_blank";
                                link.href = self.translatedFileUrl;
                                link.click();
                            }else{
                                throw new Error(res.error || "Unknown error");
                            }

                        }catch(e){
                            self.error = e.message;
                            self.loadingFileTranslation = false;
                            self.inputFile = false;
                        }
                    }else{
                        let res = JSON.parse(this.response);
                        self.error = res.error || "Unknown error";
                        self.loadingFileTranslation = false;
                        self.inputFile = false;
                    }
                }

                translateFileRequest.onerror = function() {
                    self.error = "Error while calling /translate_file";
                    self.loadingFileTranslation = false;
                    self.inputFile = false;
                };

                translateFileRequest.send(data);
            }
        }
    });

});

function getTextWidth(text) {
    var canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
    var ctx = canvas.getContext("2d");
    ctx.font = 'bold 16px sans-serif';
    var textWidth = Math.ceil(ctx.measureText(text).width);
    return textWidth;
}

function setApiKey(){
    var prevKey = localStorage.getItem("api_key") || "";
    var newKey = "";
    newKey = window.prompt("Type in your API Key. If you need an API key, contact the server operator.", prevKey);
    if (newKey === null) newKey = "";

    localStorage.setItem("api_key", newKey);
}

// @license-end
