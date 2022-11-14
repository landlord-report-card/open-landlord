import React, {useEffect, useMemo} from "react"
import { useTable, usePagination, useSortBy } from "react-table"
import { QueryClient, QueryClientProvider, useQuery } from 'react-query'
import axios from 'axios'
import SortIcon from 'mdi-react/SortIcon'
import SortAscendingIcon from 'mdi-react/SortAscendingIcon'
import SortDescendingIcon from 'mdi-react/SortDescendingIcon'
import ReactTablePagination from './ReactTablePagination'


const queryClient = new QueryClient()

const initialState = {
    queryPageIndex: 0,
    queryPageSize: 10,
    totalCount: 0,
    queryPageSortBy: [{id: 'eviction_count', desc: true}],
};

const PAGE_CHANGED = 'PAGE_CHANGED'
const PAGE_SIZE_CHANGED = 'PAGE_SIZE_CHANGED'
const PAGE_SORT_CHANGED = 'PAGE_SORT_CHANGED'
const TOTAL_COUNT_CHANGED = 'TOTAL_COUNT_CHANGED'

const reducer = (state, { type, payload }) => {
  switch (type) {
    case PAGE_CHANGED:
        return {
            ...state,
            queryPageIndex: payload,
        };
    case PAGE_SIZE_CHANGED:
        return {
            ...state,
            queryPageSize: payload,
        };
    case PAGE_SORT_CHANGED:
        return {
            ...state,
            queryPageSortBy: payload,
        };
    case TOTAL_COUNT_CHANGED:
        return {
            ...state,
            totalCount: payload,
        };
    default:
      throw new Error(`Unhandled action type: ${type}`)
  }
};


const fetchLandlordData = async (page, pageSize, pageSortBy) => {
    let paramStr = ''
    if( pageSortBy.length > 0 ) {
        const sortParams = pageSortBy[0];
        const sortByDir = sortParams.desc ? 'desc' : 'asc'
        paramStr = `${paramStr}&sortBy=${sortParams.id}&sortDirection=${sortByDir}`
    }
    try {
        const response = await axios.get(
        `/api/landlords/top/?pageNumber=${page+1}&pageSize=${pageSize}${paramStr}`
        );
        const results = response.data.landlords;
        const total_results = response.data.total_results;
        const data = {
            results: results,
            count: total_results
        };
        return data;
    } catch (e) {
        throw new Error(`API error:${e?.message}`)
    }
}


export const USERS_COLUMNS = [
    {
        Header: "Name",
        accessor: "name",
        Cell: props =><a href={"landlord/" + props.row.original.id}> {props.value} </a>    },
    {
        Header: "Address",
        accessor: "address",
    },
    {
        Header: "ID",
        accessor: "id",
    },
    {
        Header: "Tenant Complaints",
        accessor: "tenant_complaints_count",
        sortDescFirst: true,
    },
    {
        Header: "Property Count",
        accessor: "property_count",
        sortDescFirst: true
    },
    {
        Header: "Code Violations Count",
        accessor: "code_violations_count",
        sortDescFirst: true
    },
    {
        Header: "Police Incidents Count",
        accessor: "police_incidents_count",
        sortDescFirst: true
    },
    {
        Header: "Eviction Count",
        accessor: "eviction_count",
        sortDescFirst: true
    },    
    {
        Header: "Grade",
        accessor: "grade",
        sortDescFirst: true
    },    
]

const Sorting = ({ column }) => (
    <span className="react-table__column-header sortable">
      {column.isSortedDesc === undefined ? (
        <SortIcon />
      ) : (
        <span>
          {column.isSortedDesc
            ? <SortAscendingIcon />
            : <SortDescendingIcon />}
        </span>
      )}
    </span>
);


const DataTable = () => {
    let columns = useMemo( () => USERS_COLUMNS, [])

    const [{ queryPageIndex, queryPageSize, totalCount, queryPageSortBy }, dispatch] =
    React.useReducer(reducer, initialState);

    const { isLoading, error, data, isSuccess } = useQuery(
        ['users', queryPageIndex, queryPageSize, queryPageSortBy],
        () => fetchLandlordData(queryPageIndex, queryPageSize, queryPageSortBy),
        {
            keepPreviousData: false,
            staleTime: Infinity,
        }
    );

    const totalPageCount = Math.ceil(totalCount / queryPageSize)

    const {
        getTableProps,
        getTableBodyProps,
        headerGroups,
        rows,
        prepareRow,
        page,
        pageCount,
        pageOptions,
        gotoPage,
        previousPage,
        canPreviousPage,
        nextPage,
        canNextPage,
        setPageSize,
        state: { pageIndex, pageSize, sortBy }
    } = useTable({
        columns,
        data: data?.results || [],
        initialState: {
            pageIndex: queryPageIndex,
            pageSize: queryPageSize,
            sortBy: queryPageSortBy,
            hiddenColumns: ['id']
        },
        manualPagination: true,
        pageCount: data ? totalPageCount : null,
        autoResetSortBy: false,
        autoResetExpanded: false,
        autoResetPage: false,
        disableSortRemove: true,
    },
    useSortBy,
    usePagination,
    );
    const manualPageSize = []

    useEffect(() => {
        dispatch({ type: PAGE_CHANGED, payload: pageIndex });
    }, [pageIndex]);

    useEffect(() => {
        dispatch({ type: PAGE_SIZE_CHANGED, payload: pageSize });
        gotoPage(0);
    }, [pageSize, gotoPage]);

    useEffect(() => {
        dispatch({ type: PAGE_SORT_CHANGED, payload: sortBy });
        gotoPage(0);
    }, [sortBy, gotoPage]);

    useEffect(() => {
        if (data?.count) {
            dispatch({
            type: TOTAL_COUNT_CHANGED,
            payload: data.count,
            });
        }
    }, [data?.count]);

    if (error) {
        return <p>Error</p>;
    }

    if (isLoading) {
        return <p>Loading...</p>;
    }
    if(isSuccess)
    return (
            <>
                <div className='table react-table'>
                    {
                        typeof data?.count === 'undefined' && <p>No results found</p>
                    }
                    {data?.count && 
                    <>
                    <table {...getTableProps()} className="table">
                        <thead>
                            {headerGroups.map( (headerGroup) => (
                                <tr {...headerGroup.getHeaderGroupProps()}>
                                    {headerGroup.headers.map( column => (
                                        <th {...column.getHeaderProps(column.getSortByToggleProps())}>
                                            {column.render('Header')}
                                            {column.isSorted ? <Sorting column={column} /> : ''}
                                        </th>
                                    ))}
                                </tr>
                            ))}
                        </thead>
                        <tbody className="table table--bordered" {...getTableBodyProps()}>
                            {page.map( row => {
                                prepareRow(row);
                                return (
                                    <tr {...row.getRowProps()}>
                                        {
                                            row.cells.map( cell => {
                                                return <td {...cell.getCellProps()}><span>{cell.render('Cell')}</span></td>
                                            })
                                        }
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                    </>
                }
                </div>
                {(rows.length > 0) && (
                    <>
                        <ReactTablePagination
                            page={page}
                            gotoPage={gotoPage}
                            previousPage={previousPage}
                            nextPage={nextPage}
                            canPreviousPage={canPreviousPage}
                            canNextPage={canNextPage}
                            pageOptions={pageOptions}
                            pageSize={pageSize}
                            pageIndex={pageIndex}
                            pageCount={pageCount}
                            setPageSize={setPageSize}
                            manualPageSize={manualPageSize}
                            dataLength={totalCount}
                        />
                        <div className="pagination justify-content-end mt-2">
                            <span>
                            Go to page:{' '}
                            <input
                                type="number"
                                value={pageIndex + 1}
                                onChange={(e) => {
                                const page = e.target.value ? Number(e.target.value) - 1 : 0;
                                gotoPage(page);
                                }}
                                style={{ width: '100px' }}
                            />
                            </span>{' '}
                            <select
                            value={pageSize}
                            onChange={(e) => {
                                setPageSize(Number(e.target.value));
                            }}
                            >
                            {[10, 25, 50, 100].map((pageSize) => (
                                <option key={pageSize} value={pageSize}>
                                Results Per Page: {pageSize}
                                </option>
                            ))}
                            </select>
                        </div>
                    </>
                )}
            </>
    )
}


export default function Top() {    
	return (
        <QueryClientProvider client={queryClient}>
            <DataTable />
        </QueryClientProvider>
        )
}