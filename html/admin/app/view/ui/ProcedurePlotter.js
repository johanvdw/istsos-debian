/*
 * File: app/view/ui/ProcedurePlotter.js
 *
 * This file was generated by Ext Designer version 1.2.3.
 * http://www.sencha.com/products/designer/
 *
 * This file will be auto-generated each and everytime you export.
 *
 * Do NOT hand edit this file.
 */

Ext.define('istsos.view.ui.ProcedurePlotter', {
    extend: 'Ext.form.Panel',

    border: 0,
    id: 'plotdatafrm',
    padding: '5 10 0 10',
    title: '',

    initComponent: function() {
        var me = this;

        Ext.applyIf(me, {
            items: [
                {
                    xtype: 'fieldcontainer',
                    border: 0,
                    defaults: {
                        flex: 1,
                        hideLabel: true
                    },
                    layout: {
                        type: 'hbox'
                    },
                    fieldLabel: 'From',
                    labelWidth: 35,
                    anchor: '100%',
                    items: [
                        {
                            xtype: 'datefield',
                            id: 'oeBegin',
                            name: 'begin',
                            format: 'Y-m-d',
                            flex: 0.3
                        },
                        {
                            xtype: 'timefield',
                            id: 'oeBeginTime',
                            name: 'begintime',
                            fieldLabel: 'Label',
                            format: 'H:i ',
                            increment: 10,
                            flex: 0.2
                        },
                        {
                            xtype: 'label',
                            height: 22,
                            padding: '2px 0px 0px 10px',
                            width: 30,
                            text: 'To:',
                            flex: 0
                        },
                        {
                            xtype: 'datefield',
                            id: 'oeEnd',
                            name: 'end',
                            fieldLabel: 'Label',
                            format: 'Y-m-d',
                            flex: 0.3
                        },
                        {
                            xtype: 'timefield',
                            id: 'oeEndTime',
                            name: 'endtime',
                            fieldLabel: 'Label',
                            format: 'H:i ',
                            increment: 10,
                            flex: 0.2
                        },
                        {
                            xtype: 'label',
                            height: 22,
                            padding: '2px 0px 0px 10px',
                            width: 70,
                            text: 'Property:',
                            flex: 0
                        },
                        {
                            xtype: 'combobox',
                            id: 'oeCbObservedProperty',
                            name: 'observedproperty',
                            fieldLabel: 'Property',
                            labelWidth: 70,
                            displayField: 'name',
                            queryMode: 'local',
                            store: 'observedproperties',
                            valueField: 'definition',
                            flex: 0.6
                        },
                        {
                            xtype: 'button',
                            disabled: true,
                            id: 'btnPlot',
                            text: 'Plot',
                            flex: 0.4
                        }
                    ]
                }
            ]
        });

        me.callParent(arguments);
    }
});