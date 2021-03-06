/*
 * File: app/view/ui/ObservationEditor.js
 *
 * This file was generated by Ext Designer version 1.2.3.
 * http://www.sencha.com/products/designer/
 *
 * This file will be auto-generated each and everytime you export.
 *
 * Do NOT hand edit this file.
 */

Ext.define('istsos.view.ui.ObservationEditor', {
    extend: 'Ext.panel.Panel',

    border: 0,
    height: 600,
    width: 900,
    layout: {
        type: 'border'
    },
    bodyStyle: 'background-color: transparent;',
    title: '',

    initComponent: function() {
        var me = this;

        Ext.applyIf(me, {
            items: [
                {
                    xtype: 'form',
                    border: 0,
                    height: 140,
                    id: 'oeSettings',
                    bodyPadding: 10,
                    title: '',
                    region: 'north',
                    items: [
                        {
                            xtype: 'fieldset',
                            title: 'Choose the procedure',
                            items: [
                                {
                                    xtype: 'fieldcontainer',
                                    height: 30,
                                    layout: {
                                        align: 'stretch',
                                        type: 'hbox'
                                    },
                                    fieldLabel: 'Label',
                                    hideLabel: true,
                                    anchor: '100%',
                                    items: [
                                        {
                                            xtype: 'combobox',
                                            id: 'cmbServices',
                                            fieldLabel: 'Service',
                                            displayField: 'service',
                                            store: 'storeServices',
                                            valueField: 'service',
                                            flex: 1
                                        },
                                        {
                                            xtype: 'combobox',
                                            disabled: true,
                                            id: 'oeCbOffering',
                                            name: 'offering',
                                            fieldLabel: 'Offering',
                                            labelAlign: 'right',
                                            labelWidth: 60,
                                            displayField: 'name',
                                            queryMode: 'local',
                                            store: 'offerings',
                                            valueField: 'name',
                                            flex: 1
                                        },
                                        {
                                            xtype: 'combobox',
                                            disabled: true,
                                            id: 'oeCbProcedure',
                                            name: 'procedure',
                                            fieldLabel: 'Procedure',
                                            labelAlign: 'right',
                                            labelWidth: 80,
                                            displayField: 'name',
                                            queryMode: 'local',
                                            store: 'procedurelist',
                                            valueField: 'name',
                                            flex: 1
                                        },
                                        {
                                            xtype: 'combobox',
                                            disabled: true,
                                            id: 'oeCbObservedProperty',
                                            name: 'observedproperty',
                                            fieldLabel: 'Property',
                                            labelAlign: 'right',
                                            labelWidth: 80,
                                            displayField: 'name',
                                            queryMode: 'local',
                                            store: 'observedproperties',
                                            valueField: 'name',
                                            flex: 1
                                        }
                                    ]
                                },
                                {
                                    xtype: 'fieldcontainer',
                                    height: 25,
                                    defaults: {
                                        flex: 1,
                                        hideLabel: true
                                    },
                                    layout: {
                                        align: 'stretch',
                                        type: 'hbox'
                                    },
                                    fieldLabel: 'Time period',
                                    anchor: '100%',
                                    items: [
                                        {
                                            xtype: 'datefield',
                                            disabled: true,
                                            id: 'oeBegin',
                                            name: 'begin',
                                            flex: 1
                                        },
                                        {
                                            xtype: 'timefield',
                                            disabled: true,
                                            id: 'oeBeginTime',
                                            name: 'begintime',
                                            value: '00:00',
                                            fieldLabel: 'Label',
                                            format: 'G:i',
                                            increment: 10,
                                            flex: 1
                                        },
                                        {
                                            xtype: 'container',
                                            html: '<div style=\'text-align: center; width: 100%;\'>-</div>',
                                            padding: '5 0 0 0 ',
                                            width: 20,
                                            layout: {
                                                type: 'fit'
                                            },
                                            flex: 0
                                        },
                                        {
                                            xtype: 'datefield',
                                            disabled: true,
                                            id: 'oeEnd',
                                            name: 'end',
                                            fieldLabel: 'Label',
                                            flex: 1
                                        },
                                        {
                                            xtype: 'timefield',
                                            disabled: true,
                                            id: 'oeEndTime',
                                            name: 'endtime',
                                            value: '00:00',
                                            fieldLabel: 'Label',
                                            format: 'G:i',
                                            increment: 10,
                                            flex: 1
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    dockedItems: [
                        {
                            xtype: 'toolbar',
                            ui: 'footer',
                            dock: 'bottom',
                            layout: {
                                align: 'middle',
                                pack: 'center',
                                type: 'hbox'
                            },
                            items: [
                                {
                                    xtype: 'button',
                                    id: 'oeBtnReset',
                                    text: 'Reset'
                                },
                                {
                                    xtype: 'button',
                                    id: 'oeBtnLoad',
                                    text: 'Load'
                                }
                            ]
                        }
                    ]
                },
                {
                    xtype: 'panel',
                    border: 0,
                    id: 'oeEditor',
                    layout: {
                        type: 'fit'
                    },
                    title: '',
                    region: 'center'
                }
            ]
        });

        me.callParent(arguments);
    }
});