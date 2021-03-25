odoo.define('materiales_stock_orders.excel_file', function (require) {
    "use strict";

var ActionManager = require('web.ActionManager');
var framework = require('web.framework');
var session = require('web.session');

ActionManager.include({

   
    _executexlsxReportDownloadAction: function (action) {
        framework.blockUI();
        var def = $.Deferred();
        session.get_file({
            url: '/stock_order_xlsx_reports',
            data: action.data,
            success: def.resolve.bind(def),
            error: (error) => this.call('crash_manager', 'rpc_error', error),
            complete: framework.unblockUI,
        });
        return def;
    },

    _handleAction: function (action, options) {

        if (action.type === 'ir_actions_xlsx_download') {
            return this._executexlsxReportDownloadAction(action, options);
        }
        return this._super.apply(this, arguments);
    },
});

});